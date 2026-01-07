import asyncio
import hashlib
import json
import os
import re
import secrets
import uuid
import traceback
import aiopg
import pypandoc
import pytz
from collections import Counter
from aiopg.connection import psycopg2
from datetime import datetime, timezone, timedelta

from mayday.data.default_config import DEFAULT_SERVICES, DEFAULT_FAQS, DEFAULT_DESCRIPTIONS, AVAILABLE_ICONS
from mayday.logger import logger
from mayday.business_api import GoogleBusinessAPI


POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USERNAME = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
SESSION_TIMEOUT = os.environ.get("SESSION_TIMEOUT", 60) # Minutes


class PostgresDataLayer:
    def __init__(self):
        with open(os.path.join(os.getcwd(), "mayday/data/schema.json"), "r") as json_schema:
            self.schema = json.load(json_schema)
        self.pool = None

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using PBKDF2 with SHA-256"""
        salt = secrets.token_hex(16)
        pwdh = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${pwdh.hex()}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, stored_hash = password_hash.split('$')
            pwdh = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwdh.hex() == stored_hash
        except (ValueError, AttributeError):
            return False
    
    def dsn(self, dbname=POSTGRES_DB, username=POSTGRES_USERNAME, password=POSTGRES_PASSWORD):
        return f"dbname={dbname} user={username} password="\
               f"{password} host={POSTGRES_HOST} port={POSTGRES_PORT}"
    
    async def init(self):
        # Initialize the persistent connection pool
        if self.pool is None:
            self.pool = await aiopg.create_pool(self.dsn(), minsize=2, maxsize=10)
            logger.info("Database connection pool initialized")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
                tables = [x[0] for x in await cur.fetchall() if x]

                init = ""
                for table_name, schema_values in self.schema.items():
                    if table_name not in tables:
                        table_schema = [' '.join(tup) for tup in list(zip(list(schema_values.keys()), list(schema_values.values())))]
                        init += f"CREATE TABLE {table_name} ({','.join(table_schema)});"
                    elif table_name == 'blog_posts':
                        # Handle migration for blog_posts table
                        await cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'blog_posts'")
                        columns = [row[0] for row in await cur.fetchall()]

                        # If old 'image' column exists but not 'image_data', migrate
                        if 'image' in columns and 'image_data' not in columns:
                            init += "ALTER TABLE blog_posts RENAME COLUMN image TO image_data;"

                # Handle staff to website_administrators migration
                if 'staff' in tables and 'website_administrators' not in tables:
                    # Create website_administrators table and drop staff table
                    # Note: This is a breaking change - staff data will be lost
                    logger.info("Migrating from staff table to website_administrators table")
                    init += "DROP TABLE IF EXISTS staff;"
                    # The website_administrators table will be created above if needed

                # Handle website_administrators table password_hash column migration
                if 'website_administrators' in tables:
                    # Check if password_hash column exists
                    await cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'website_administrators' AND column_name = 'password_hash'")
                    password_hash_column = await cur.fetchone()

                    if not password_hash_column:
                        logger.info("Adding password_hash column to website_administrators table")
                        init += "ALTER TABLE website_administrators ADD COLUMN password_hash TEXT;"
                        # Set a default password hash for existing administrators (they'll need to reset)
                        # Using a hash of "changeme123" as temporary password
                        default_hash = self.hash_password("changeme123")
                        init += f"UPDATE website_administrators SET password_hash = '{default_hash}' WHERE password_hash IS NULL;"
                        init += "ALTER TABLE website_administrators ALTER COLUMN password_hash SET NOT NULL;"

                    # Update unique constraints to allow duplicates for inactive users
                    logger.info("Updating unique constraints for website_administrators")
                    # Drop the old unique constraints
                    init += "ALTER TABLE website_administrators DROP CONSTRAINT IF EXISTS website_administrators_username_key;"
                    init += "ALTER TABLE website_administrators DROP CONSTRAINT IF EXISTS website_administrators_email_key;"
                    # Add partial unique indexes that only apply to active users
                    init += "CREATE UNIQUE INDEX IF NOT EXISTS website_administrators_username_active_unique ON website_administrators (LOWER(username)) WHERE is_active = true;"
                    init += "CREATE UNIQUE INDEX IF NOT EXISTS website_administrators_email_active_unique ON website_administrators (LOWER(email)) WHERE is_active = true;"
                
                if init:
                    await cur.execute(init)
            
            # Initialize default configuration after tables are created (outside the cursor context)
            await self._initialize_default_config()

    async def get_sessions(self):
        sessions = []

        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    await cur.execute("SELECT * FROM session")
                    sessions = await cur.fetchall()
        
        return sessions

    async def get_session_meta_cache(self, cookie, cache_kwarg=None):
        response = None
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT meta FROM session WHERE cookie = %s", (cookie,))
                meta = await cur.fetchone()

                if meta:
                    if cache_kwarg in meta[0]:
                        response = meta[0][cache_kwarg]
                    else:
                        response = meta[0]

        return response

    async def get_event(self, cookie):
        event = None, None
        if cookie:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("SELECT id,event,type FROM events WHERE cookie = %s", (cookie,))
                        event_query = await cur.fetchone()
                        if event_query:
                            event = event_query["event"], event_query["type"]
                            await cur.execute("DELETE FROM events WHERE id = %s", (event_query["id"],))
        
        return event

    async def create_event(self, cookie, event, event_type):
        if cookie:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        # Clear out old events
                        await cur.execute("DELETE FROM events WHERE cookie = %s", (cookie,))
                        # Insert new
                        await cur.execute("INSERT INTO events(cookie,event,type) VALUES (%s, %s, %s)", (cookie,event,event_type))

    async def create_session(self, cookie=None, username="", password=""):
        record = {
            "cookie": cookie or str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "username": username,
            "admin": False
        }

        # See if user is eligible for admin privileges
        if username and password:
            # First try website administrator authentication
            logger.debug(f"Attempting website administrator authentication for '{username}'")
            admin_auth = await self.authenticate_website_administrator(username, password)
            if admin_auth:
                logger.info(f"✓ SUCCESSFUL website administrator authentication for '{username}' ({admin_auth['full_name']})")
                record["admin"] = True
                record["username"] = admin_auth['username']
            else:
                # Fallback to database authentication (for backward compatibility)
                logger.debug(f"Website administrator authentication failed, trying database authentication for '{username}'")
                try:
                    test_dsn = self.dsn(
                        username=username,
                        password=password
                    )
                    async with aiopg.create_pool(test_dsn):
                        logger.info(f"✓ SUCCESSFUL database admin authentication for '{username}'")

                    record["admin"] = True

                except Exception as e:
                    logger.warning(f"✗ FAILED authentication attempt for '{username}'. Website admin auth: failed, Database auth error: {e}")
                    raise psycopg2.OperationalError from e

        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Update existing record
                    if cookie:
                        await self.update_session(cookie, record)

                    # Create new session record
                    else:
                        # Get HCP services from cache instead of calling HCP directly
                        hcp_services_data = await self.get_hcp_services()
                        services_list = []
                        if hcp_services_data and hcp_services_data.get('services'):
                            # Extract the services list from cached data structure
                            for service_category in hcp_services_data['services'].values():
                                services_list.extend(service_category)

                        record["meta"] = json.dumps({
                            "services": services_list # caching services for faster load times using cached HCP data
                        })
                        await cur.execute("INSERT INTO session VALUES(%s, %s, %s, %s, %s)", tuple(record.values()))
                        logger.info("New session created")
        
        return record["cookie"]
    
    async def update_session(self, cookie, updateargs):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if cookie in {d.pop("cookie"):d for d in await self.get_sessions()}:
                        for k,v in updateargs.items():
                            await cur.execute(f'UPDATE session SET "{k}" = %s WHERE cookie = %s', (v, cookie))

    async def delete_session(self, cookie):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    await cur.execute("DELETE FROM session WHERE cookie = %s", (cookie,))

    async def clear_all_sessions(self):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("DELETE FROM session")
                    await cur.execute("DELETE FROM events")
        logger.info("All sessions and events cleared on startup")

    async def verify_session(self, cookie, update_ts=True, delete_if_expired=False):
        cookie_is_privileged = False

        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    if cookie:
                        await cur.execute("SELECT * FROM session WHERE cookie = %s", (cookie,))
                        session = await cur.fetchone()

                        if session:
                            cookie_is_privileged = session["admin"] == True
                            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=int(SESSION_TIMEOUT))
                            
                            # Session cookie is still valid, lets update the session timestamp
                            if pytz.UTC.localize(session["timestamp"]) > cutoff_time:
                                if update_ts:
                                    await self.update_session(cookie, {"timestamp": datetime.now(timezone.utc)})
                                
                            # Session is expired. Delete session record from database
                            elif delete_if_expired:
                                logger.info(f"Session is expired. Removing session record for - {cookie}")
                                await self.delete_session(cookie)

                            # Session is expired. Revoke admin rights if applicable
                            else:
                                logger.info("Admin session expired. Revoking admin rights")
                                await self.update_session(cookie, {"admin": False})

        return cookie_is_privileged

    async def get_section_meta(self, section):
        response = None

        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    if section.lower() == "all":
                        response = {}

                        await cur.execute("SELECT name,meta FROM sections")
                        meta = await cur.fetchall()
                        for row in meta:
                            for panel in row["meta"]["panels"]:
                                panel["heading"] = pypandoc.convert_text(re.sub("\s*\[(.*)\]\s*", "", panel["heading"]), 'html', format='md')
                                panel["body"] = pypandoc.convert_text(panel["body"], 'html', format='md')
                                for sibling in panel["siblings"]:
                                    sibling["heading"] = pypandoc.convert_text(re.sub("\s*\[(.*)\]\s*", "", sibling["heading"]), 'html', format='md')
                                    sibling["body"] = pypandoc.convert_text(sibling["body"], 'html', format='md')
                        
                        response = {x["name"]: x["meta"] for x in meta}

                    else:
                        response = ""

                        await cur.execute("SELECT meta FROM sections WHERE name = %s", (section,))
                        section_meta = await cur.fetchone()
                        panels_markdown = ""
                        if section_meta:
                            for panel_dict in section_meta["meta"]["panels"]:
                                panels_markdown += f'{panel_dict["heading"]}\n{panel_dict["body"]}'
                                for sibling in panel_dict["siblings"]:
                                    panels_markdown += f'{sibling["heading"]}\n{sibling["body"]}'

                        response = panels_markdown

        return response
    
    async def update_section_meta(self, section, panels):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    meta = {"panels": []}

                    grid_start = None

                    for heading, body in panels:
                        panel_attributes = {
                            "heading": heading,
                            "body": body,
                            "siblings": [],
                            "options": {"grid": False}
                        }

                        # Check heading for panel options
                        panel_options = re.findall(r"\s*\[(.*)\]\s*", heading)
                        if panel_options:
                            # New grid starting
                            if grid_start:
                                grid_start = None

                            panel_options = panel_options[0].split(" ")

                            # Currently only supports grid option
                            if panel_options[0] == "grid":
                                grid_start = len(meta["panels"])
                                panel_attributes["options"]["grid"] = True
                                panel_attributes["options"]["grid_style"] = f"grid-template-columns: {' '.join(panel_options[1:])}"

                        elif grid_start is not None:
                            meta["panels"][grid_start]["siblings"].append(panel_attributes)
                            continue

                        meta["panels"].append(panel_attributes)

                    if await self.get_section_meta(section):
                        await cur.execute("UPDATE sections SET meta = %s WHERE name = %s", (json.dumps(meta), section))
                    else:
                        await cur.execute("INSERT INTO sections VALUES(%s, %s)", (section, json.dumps(meta)))
    
    async def get_website_administrators(self):
        administrators = []
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("SELECT id, username, email, full_name, is_active, created_at, last_login FROM website_administrators WHERE is_active = true ORDER BY created_at")
                        administrators = await cur.fetchall()
        except Exception as e:
            # If website_administrators table doesn't exist yet, return empty list
            logger.debug(f"Could not fetch website administrators: {e}")
            administrators = []

        return administrators

    async def create_website_administrator(self, username, email, full_name, password):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Check if username or email already exists among ACTIVE administrators
                    await cur.execute("SELECT id FROM website_administrators WHERE (LOWER(username) = %s OR LOWER(email) = %s) AND is_active = true", (username.lower(), email.lower()))
                    if await cur.fetchone():
                        raise ValueError("Username or email already exists")

                    # Hash the password
                    password_hash = self.hash_password(password)

                    await cur.execute("INSERT INTO website_administrators(username, email, full_name, password_hash) VALUES(%s, %s, %s, %s) RETURNING id", (username, email, full_name, password_hash))
                    admin_id = (await cur.fetchone())[0]
                    return admin_id

    async def update_website_administrator(self, admin_id, username, email, full_name, password=None):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Check if username or email already exists for different ACTIVE admin
                    await cur.execute("SELECT id FROM website_administrators WHERE (LOWER(username) = %s OR LOWER(email) = %s) AND id != %s AND is_active = true", (username.lower(), email.lower(), admin_id))
                    if await cur.fetchone():
                        raise ValueError("Username or email already exists")

                    if password:
                        # Update with new password
                        password_hash = self.hash_password(password)
                        await cur.execute("UPDATE website_administrators SET username = %s, email = %s, full_name = %s, password_hash = %s WHERE id = %s", (username, email, full_name, password_hash, admin_id))
                    else:
                        # Update without changing password
                        await cur.execute("UPDATE website_administrators SET username = %s, email = %s, full_name = %s WHERE id = %s", (username, email, full_name, admin_id))

    async def delete_website_administrator(self, admin_id):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Soft delete by setting is_active to false
                    await cur.execute("UPDATE website_administrators SET is_active = false WHERE id = %s", (admin_id,))

    async def authenticate_website_administrator(self, username, password):
        """Authenticate a website administrator by username and password"""
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("SELECT id, username, password_hash, full_name FROM website_administrators WHERE LOWER(username) = %s AND is_active = true", (username.lower(),))
                        admin = await cur.fetchone()

                        if admin and self.verify_password(password, admin['password_hash']):
                            # Update last login timestamp
                            await cur.execute("UPDATE website_administrators SET last_login = CURRENT_TIMESTAMP WHERE id = %s", (admin['id'],))
                            return {
                                'id': admin['id'],
                                'username': admin['username'],
                                'full_name': admin['full_name']
                            }
                        return None
        except Exception as e:
            # If website_administrators table doesn't exist or other DB error, return None
            # This allows fallback to database authentication
            logger.debug(f"Website administrator authentication failed: {e}")
            return None

    async def create_database_backup(self):
        """Create a backup of the database using Python SQL export"""

        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mayday_backup_{timestamp}.json"
        backup_path = os.path.join(os.getcwd(), "backups", backup_filename)

        # Ensure backups directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        try:
            backup_data = {
                "timestamp": timestamp,
                "database": POSTGRES_DB,
                "version": "1.0",
                "tables": {}
            }

            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        # Get all table names
                        await cur.execute("""
                            SELECT tablename FROM pg_catalog.pg_tables
                            WHERE schemaname = 'public'
                            ORDER BY tablename
                        """)
                        tables = [row['tablename'] for row in await cur.fetchall()]

                        logger.info(f"Backing up {len(tables)} tables: {tables}")

                        # Export each table
                        for table_name in tables:
                            try:
                                # Get table structure
                                await cur.execute(f"""
                                    SELECT column_name, data_type, is_nullable, column_default
                                    FROM information_schema.columns
                                    WHERE table_name = %s AND table_schema = 'public'
                                    ORDER BY ordinal_position
                                """, (table_name,))
                                columns = await cur.fetchall()

                                # Get table data
                                await cur.execute(f'SELECT * FROM "{table_name}" ORDER BY 1')
                                rows = await cur.fetchall()

                                backup_data["tables"][table_name] = {
                                    "structure": [dict(col) for col in columns],
                                    "data": [dict(row) for row in rows],
                                    "row_count": len(rows)
                                }

                                logger.info(f"Backed up table {table_name}: {len(rows)} rows")

                            except Exception as table_error:
                                logger.error(f"Error backing up table {table_name}: {table_error}")
                                backup_data["tables"][table_name] = {
                                    "error": str(table_error),
                                    "row_count": 0
                                }

            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, (datetime.datetime, datetime.date)):
                    return obj.isoformat()
                elif hasattr(obj, '__dict__'):
                    return str(obj)
                return str(obj)

            # Write backup to file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=json_serializer, ensure_ascii=False)

            # Get file size for confirmation
            file_size = os.path.getsize(backup_path)
            logger.info(f"Database backup created successfully: {backup_filename} ({file_size} bytes)")

            return {
                "success": True,
                "filename": backup_filename,
                "filepath": backup_path,
                "size": file_size,
                "timestamp": timestamp,
                "tables_backed_up": len([t for t in backup_data["tables"] if "error" not in backup_data["tables"][t]])
            }

        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def restore_database_backup(self, backup_filename):
        """Restore database from a JSON backup file"""

        backup_path = os.path.join(os.getcwd(), "backups", backup_filename)

        # Check if backup file exists
        if not os.path.exists(backup_path):
            return {
                "success": False,
                "error": f"Backup file not found: {backup_filename}"
            }

        try:
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            if "tables" not in backup_data:
                return {
                    "success": False,
                    "error": "Invalid backup file format"
                }

            restored_tables = 0
            failed_tables = []

            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        # Start transaction
                        await cur.execute("BEGIN")

                        try:
                            # Process each table in the backup
                            for table_name, table_data in backup_data["tables"].items():
                                if "error" in table_data:
                                    logger.warning(f"Skipping table {table_name} due to backup error")
                                    continue

                                try:
                                    # Clear existing data
                                    await cur.execute(f'DELETE FROM "{table_name}"')

                                    # Insert backed up data
                                    if table_data.get("data") and len(table_data["data"]) > 0:
                                        # Get column names from the first row
                                        sample_row = table_data["data"][0]
                                        columns = list(sample_row.keys())

                                        # Create parameterized insert statement
                                        placeholders = ','.join(['%s'] * len(columns))
                                        column_names = ','.join([f'"{col}"' for col in columns])
                                        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'

                                        # Prepare data for insertion
                                        rows_to_insert = []
                                        for row in table_data["data"]:
                                            row_values = []
                                            for col in columns:
                                                value = row.get(col)
                                                # Handle datetime strings
                                                if isinstance(value, str) and ('T' in value or value.endswith('Z')):
                                                    try:
                                                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                                                        row_values.append(value)
                                                    except Exception:
                                                        row_values.append(value)
                                                else:
                                                    row_values.append(value)
                                            rows_to_insert.append(tuple(row_values))

                                        # Execute batch insert
                                        await cur.executemany(insert_sql, rows_to_insert)

                                        logger.info(f"Restored table {table_name}: {len(rows_to_insert)} rows")
                                    else:
                                        logger.info(f"Restored table {table_name}: 0 rows (empty table)")

                                    restored_tables += 1

                                except Exception as table_error:
                                    logger.error(f"Error restoring table {table_name}: {table_error}")
                                    failed_tables.append(f"{table_name}: {str(table_error)}")
                                    # Continue with other tables instead of failing completely

                            # Commit transaction
                            await cur.execute("COMMIT")

                            if failed_tables:
                                logger.warning(f"Restore completed with errors. Failed tables: {failed_tables}")
                                return {
                                    "success": True,
                                    "filename": backup_filename,
                                    "message": f"Database partially restored - {restored_tables} tables successful",
                                    "warnings": failed_tables,
                                    "tables_restored": restored_tables
                                }
                            else:
                                logger.info(f"Database restored successfully from: {backup_filename}")
                                return {
                                    "success": True,
                                    "filename": backup_filename,
                                    "message": f"Database restored successfully - {restored_tables} tables",
                                    "tables_restored": restored_tables
                                }

                        except Exception as transaction_error:
                            # Rollback on major error
                            await cur.execute("ROLLBACK")
                            raise transaction_error

        except Exception as e:
            logger.error(f"Database restore error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_database_backups(self):
        """List available database backup files"""

        backups_dir = os.path.join(os.getcwd(), "backups")
        backups = []

        try:
            if os.path.exists(backups_dir):
                for filename in os.listdir(backups_dir):
                    # Support both JSON (new) and SQL (legacy) backup files
                    if filename.startswith("mayday_backup_") and (filename.endswith(".json") or filename.endswith(".sql")):
                        filepath = os.path.join(backups_dir, filename)
                        stat = os.stat(filepath)

                        backup_type = "JSON" if filename.endswith(".json") else "SQL"

                        backups.append({
                            "filename": filename,
                            "size": stat.st_size,
                            "created": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "age_hours": (datetime.datetime.now().timestamp() - stat.st_mtime) / 3600,
                            "type": backup_type
                        })

                # Sort by creation time (newest first)
                backups.sort(key=lambda x: x["filename"], reverse=True)

            return {
                "success": True,
                "backups": backups
            }

        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_database_backup(self, backup_filename):
        """Delete a database backup file"""

        backup_path = os.path.join(os.getcwd(), "backups", backup_filename)

        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"Backup deleted: {backup_filename}")
                return {
                    "success": True,
                    "message": f"Backup {backup_filename} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Backup file not found: {backup_filename}"
                }

        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_descriptions(self):
        descriptions = {}
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("SELECT section, text FROM descriptions")
                        results = await cur.fetchall()
                        descriptions = {row['section']: row['text'] for row in results}
                        logger.info(f"Retrieved descriptions: {descriptions}")
        except Exception as e:
            logger.error(f"Error getting descriptions: {e}")
        return descriptions

    async def update_description(self, section, text):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT section FROM descriptions WHERE section = %s", (section,))
                    exists = await cur.fetchone()
                    
                    if exists:
                        await cur.execute("UPDATE descriptions SET text = %s WHERE section = %s", (text, section))
                    else:
                        await cur.execute("INSERT INTO descriptions (section, text) VALUES (%s, %s)", (section, text))

    # Initialization methods
    async def _initialize_default_config(self):
        """Initialize default configuration if not present, without overwriting existing data"""
        try:
            logger.info("Initializing default configuration...")
            
            # Initialize default descriptions
            await self._initialize_descriptions()
            
            # Initialize default services
            await self._initialize_services()
            
            # Initialize default FAQs
            await self._initialize_faqs()
            
            logger.info("Default configuration initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing default configuration: {e}")
    
    async def _initialize_descriptions(self):
        """Initialize default descriptions if they don't exist"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    for section, text in DEFAULT_DESCRIPTIONS.items():
                        await cur.execute("SELECT section FROM descriptions WHERE section = %s", (section,))
                        if not await cur.fetchone():
                            await cur.execute("INSERT INTO descriptions (section, text) VALUES (%s, %s)", (section, text))
                            logger.info(f"Initialized description for {section}")
    
    async def _initialize_services(self):
        """Initialize default services if none exist"""
        try:
            logger.info("Starting services initialization...")
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        # Check if services table exists
                        await cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = 'services'
                            )
                        """)
                        table_exists = (await cur.fetchone())[0]
                        logger.info(f"Services table exists: {table_exists}")
                        
                        if not table_exists:
                            logger.error("Services table does not exist!")
                            return
                        
                        # Check current count
                        await cur.execute("SELECT COUNT(*) FROM services WHERE is_active = true")
                        count = (await cur.fetchone())[0]
                        logger.info(f"Current active services count: {count}")
                        
                        if count == 0:
                            logger.info(f"Inserting {len(DEFAULT_SERVICES)} default services...")
                            for i, service in enumerate(DEFAULT_SERVICES):
                                logger.info(f"Inserting service {i+1}: {service['title']}")
                                try:
                                    await cur.execute(
                                        "INSERT INTO services (title, description, icon, display_order) VALUES (%s, %s, %s, %s)",
                                        (service['title'], service['description'], service['icon'], service['display_order'])
                                    )
                                except Exception as insert_error:
                                    logger.error(f"Error inserting service '{service['title']}': {insert_error}")
                                    raise
                            
                            # Verify insertion
                            await cur.execute("SELECT COUNT(*) FROM services WHERE is_active = true")
                            new_count = (await cur.fetchone())[0]
                            logger.info(f"Services after insertion: {new_count}")
                            logger.info(f"Successfully initialized {len(DEFAULT_SERVICES)} default services")
                        else:
                            logger.info(f"Services already exist ({count} found), skipping initialization")
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    async def _initialize_faqs(self):
        """Initialize default FAQs if none exist"""
        try:
            logger.info("Starting FAQs initialization...")
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        # Check if faqs table exists
                        await cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = 'faqs'
                            )
                        """)
                        table_exists = (await cur.fetchone())[0]
                        logger.info(f"FAQs table exists: {table_exists}")
                        
                        if not table_exists:
                            logger.error("FAQs table does not exist!")
                            return
                        
                        await cur.execute("SELECT COUNT(*) FROM faqs WHERE is_active = true")
                        count = (await cur.fetchone())[0]
                        logger.info(f"Current active FAQs count: {count}")
                        
                        if count == 0:
                            logger.info(f"Inserting {len(DEFAULT_FAQS)} default FAQs...")
                            for faq in DEFAULT_FAQS:
                                await cur.execute(
                                    "INSERT INTO faqs (question, answer, display_order) VALUES (%s, %s, %s)",
                                    (faq['question'], faq['answer'], faq['display_order'])
                                )
                            logger.info(f"Successfully initialized {len(DEFAULT_FAQS)} default FAQs")
                        else:
                            logger.info(f"FAQs already exist ({count} found), skipping initialization")
        except Exception as e:
            logger.error(f"Error initializing FAQs: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")

    # Services CRUD operations
    async def get_services(self):
        """Get all active services ordered by display_order"""
        services = []
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute(
                            "SELECT id, title, description, icon, display_order FROM services WHERE is_active = true ORDER BY display_order, id"
                        )
                        services = await cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting services: {e}")
        return services
    
    async def create_service(self, title, description, icon, display_order=0):
        """Create a new service with proper display order handling"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # If display_order is 0 or not specified, find the next available order
                    if display_order == 0:
                        await cur.execute(
                            "SELECT COALESCE(MAX(display_order), 0) + 1 FROM services WHERE is_active = true"
                        )
                        display_order = (await cur.fetchone())[0]
                    else:
                        # Check if the specified display_order already exists
                        await cur.execute(
                            "SELECT COUNT(*) FROM services WHERE display_order = %s AND is_active = true",
                            (display_order,)
                        )
                        existing_count = (await cur.fetchone())[0]
                        
                        if existing_count > 0:
                            # Increment display_order for all services >= specified order
                            await cur.execute(
                                "UPDATE services SET display_order = display_order + 1, updated_at = CURRENT_TIMESTAMP WHERE display_order >= %s AND is_active = true",
                                (display_order,)
                            )
                    
                    # Insert the new service
                    await cur.execute(
                        "INSERT INTO services (title, description, icon, display_order) VALUES (%s, %s, %s, %s) RETURNING id",
                        (title, description, icon, display_order)
                    )
                    service_id = (await cur.fetchone())[0]
                    return service_id
    
    async def update_service(self, service_id, title, description, icon, display_order=0):
        """Update an existing service with proper display order handling"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Get current service info
                    await cur.execute(
                        "SELECT display_order FROM services WHERE id = %s",
                        (service_id,)
                    )
                    current_service = await cur.fetchone()
                    if not current_service:
                        return False
                    
                    current_display_order = current_service[0]
                    
                    # If display_order is 0, keep current order
                    if display_order == 0:
                        display_order = current_display_order
                    
                    # If display order is changing, handle reordering
                    if display_order != current_display_order:
                        # Check if the new display_order already exists (excluding current service)
                        await cur.execute(
                            "SELECT COUNT(*) FROM services WHERE display_order = %s AND is_active = true AND id != %s",
                            (display_order, service_id)
                        )
                        existing_count = (await cur.fetchone())[0]
                        
                        if existing_count > 0:
                            # If moving to a higher order, shift others down
                            if display_order > current_display_order:
                                await cur.execute(
                                    "UPDATE services SET display_order = display_order - 1, updated_at = CURRENT_TIMESTAMP WHERE display_order > %s AND display_order <= %s AND is_active = true AND id != %s",
                                    (current_display_order, display_order, service_id)
                                )
                            # If moving to a lower order, shift others up
                            else:
                                await cur.execute(
                                    "UPDATE services SET display_order = display_order + 1, updated_at = CURRENT_TIMESTAMP WHERE display_order >= %s AND display_order < %s AND is_active = true AND id != %s",
                                    (display_order, current_display_order, service_id)
                                )
                    
                    # Update the service
                    await cur.execute(
                        "UPDATE services SET title = %s, description = %s, icon = %s, display_order = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (title, description, icon, display_order, service_id)
                    )
                    return True
    
    async def delete_service(self, service_id):
        """Delete a service (soft delete by setting is_active to false)"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE services SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (service_id,)
                    )
    
    async def reorder_services(self, services):
        """Reorder services based on new positions"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    for service in services:
                        await cur.execute(
                            "UPDATE services SET display_order = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND is_active = true",
                            (service['display_order'], service['id'])
                        )

    # FAQ CRUD operations
    async def get_faqs(self, limit=None, offset=0):
        """Get all active FAQs ordered by display_order"""
        faqs = []
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        query = "SELECT id, question, answer, display_order FROM faqs WHERE is_active = true ORDER BY display_order, id"
                        params = []
                        
                        if limit is not None:
                            query += " LIMIT %s"
                            params.append(limit)
                            
                        if offset > 0:
                            query += " OFFSET %s" 
                            params.append(offset)
                        
                        await cur.execute(query, params)
                        faqs = await cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting FAQs: {e}")
        return faqs
    
    async def search_faqs(self, search_term, limit=None, offset=0):
        """Search FAQs by question and answer content"""
        faqs = []
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        query = """
                            SELECT id, question, answer, display_order 
                            FROM faqs 
                            WHERE is_active = true 
                            AND (LOWER(question) LIKE LOWER(%s) OR LOWER(answer) LIKE LOWER(%s))
                            ORDER BY display_order, id
                        """
                        params = [f"%{search_term}%", f"%{search_term}%"]
                        
                        if limit is not None:
                            query += " LIMIT %s"
                            params.append(limit)
                            
                        if offset > 0:
                            query += " OFFSET %s" 
                            params.append(offset)
                        
                        await cur.execute(query, params)
                        faqs = await cur.fetchall()
        except Exception as e:
            logger.error(f"Error searching FAQs: {e}")
        return faqs
    
    async def create_faq(self, question, answer, display_order=0):
        """Create a new FAQ with proper display order handling"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # If display_order is 0 or not specified, find the next available order
                    if display_order == 0:
                        await cur.execute(
                            "SELECT COALESCE(MAX(display_order), 0) + 1 FROM faqs WHERE is_active = true"
                        )
                        display_order = (await cur.fetchone())[0]
                    else:
                        # Check if the specified display_order already exists
                        await cur.execute(
                            "SELECT COUNT(*) FROM faqs WHERE display_order = %s AND is_active = true",
                            (display_order,)
                        )
                        existing_count = (await cur.fetchone())[0]
                        
                        if existing_count > 0:
                            # Increment display_order for all FAQs >= specified order
                            await cur.execute(
                                "UPDATE faqs SET display_order = display_order + 1, updated_at = CURRENT_TIMESTAMP WHERE display_order >= %s AND is_active = true",
                                (display_order,)
                            )
                    
                    # Insert the new FAQ
                    await cur.execute(
                        "INSERT INTO faqs (question, answer, display_order) VALUES (%s, %s, %s) RETURNING id",
                        (question, answer, display_order)
                    )
                    faq_id = (await cur.fetchone())[0]
                    return faq_id
    
    async def update_faq(self, faq_id, question, answer, display_order=0):
        """Update an existing FAQ with proper display order handling"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Get current FAQ info
                    await cur.execute(
                        "SELECT display_order FROM faqs WHERE id = %s",
                        (faq_id,)
                    )
                    current_faq = await cur.fetchone()
                    if not current_faq:
                        return False
                    
                    current_display_order = current_faq[0]
                    
                    # If display_order is 0, keep current order
                    if display_order == 0:
                        display_order = current_display_order
                    
                    # If display order is changing, handle reordering
                    if display_order != current_display_order:
                        # Check if the new display_order already exists (excluding current FAQ)
                        await cur.execute(
                            "SELECT COUNT(*) FROM faqs WHERE display_order = %s AND is_active = true AND id != %s",
                            (display_order, faq_id)
                        )
                        existing_count = (await cur.fetchone())[0]
                        
                        if existing_count > 0:
                            # If moving to a higher order, shift others down
                            if display_order > current_display_order:
                                await cur.execute(
                                    "UPDATE faqs SET display_order = display_order - 1, updated_at = CURRENT_TIMESTAMP WHERE display_order > %s AND display_order <= %s AND is_active = true AND id != %s",
                                    (current_display_order, display_order, faq_id)
                                )
                            # If moving to a lower order, shift others up
                            else:
                                await cur.execute(
                                    "UPDATE faqs SET display_order = display_order + 1, updated_at = CURRENT_TIMESTAMP WHERE display_order >= %s AND display_order < %s AND is_active = true AND id != %s",
                                    (display_order, current_display_order, faq_id)
                                )
                    
                    # Update the FAQ
                    await cur.execute(
                        "UPDATE faqs SET question = %s, answer = %s, display_order = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (question, answer, display_order, faq_id)
                    )
                    return True
    
    async def delete_faq(self, faq_id):
        """Delete a FAQ (soft delete by setting is_active to false)"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE faqs SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (faq_id,)
                    )
    
    async def reorder_faqs(self, faqs):
        """Reorder FAQs based on new positions"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    for faq in faqs:
                        await cur.execute(
                            "UPDATE faqs SET display_order = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND is_active = true",
                            (faq['display_order'], faq['id'])
                        )
    
    def get_available_icons(self):
        """Get list of available icons for services"""
        return AVAILABLE_ICONS

    async def get_announcement(self):
        announcement = None
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    await cur.execute("SELECT * FROM announcement WHERE active = true ORDER BY created_at DESC LIMIT 1")
                    announcement = await cur.fetchone()
        return announcement

    async def update_announcement(self, text, announcement_type="info", active=True):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Deactivate all existing announcements
                    await cur.execute("UPDATE announcement SET active = false")
                    
                    # Insert new announcement if text is provided
                    if text and text.strip():
                        await cur.execute(
                            "INSERT INTO announcement (text, type, active) VALUES (%s, %s, %s)", 
                            (text.strip(), announcement_type, active)
                        )

    # API Data Cache Management (Generic for Google, HCP, etc.)
    async def get_cached_api_data(self, cache_type):
        """Get cached API data if it's still valid"""
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("""
                            SELECT data, cached_at, expires_at
                            FROM api_cache
                            WHERE cache_type = %s AND is_valid = true AND expires_at > CURRENT_TIMESTAMP
                            ORDER BY cached_at DESC
                            LIMIT 1
                        """, (cache_type,))
                        result = await cur.fetchone()

                        if result:
                            logger.info(f"Found valid cached {cache_type} data from {result['cached_at']}")
                            return result['data']
                        else:
                            logger.info(f"No valid cached {cache_type} data found")
                            return None
        except Exception as e:
            logger.error(f"Error getting cached {cache_type} data: {e}")
            return None

    async def set_cached_api_data(self, cache_type, data, cache_duration_hours=1):
        """Cache API data with expiration"""
        try:
            expires_at = datetime.now() + timedelta(hours=cache_duration_hours)

            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        # Invalidate old cache entries for this type
                        await cur.execute("""
                            UPDATE api_cache
                            SET is_valid = false
                            WHERE cache_type = %s AND is_valid = true
                        """, (cache_type,))

                        # Insert new cache entry
                        await cur.execute("""
                            INSERT INTO api_cache (cache_type, data, expires_at)
                            VALUES (%s, %s, %s)
                        """, (cache_type, json.dumps(data), expires_at))

                        logger.info(f"Cached {cache_type} data until {expires_at}")
        except Exception as e:
            logger.error(f"Error caching {cache_type} data: {e}")

    async def is_api_cache_expired(self, cache_type):
        """Check if API cache needs refresh"""
        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            SELECT COUNT(*) FROM api_cache
                            WHERE cache_type = %s AND is_valid = true AND expires_at > CURRENT_TIMESTAMP
                        """, (cache_type,))
                        count = (await cur.fetchone())[0]
                        return count == 0
        except Exception as e:
            logger.error(f"Error checking cache expiration for {cache_type}: {e}")
            return True  # Assume expired on error

    async def get_google_rating(self):
        """Get Google rating from cache, fallback to scraping if needed"""
        # Try to get from cache first
        cached_data = await self.get_cached_api_data('google_rating')
        if cached_data:
            return cached_data

        # If no cache, return default and let background task handle it
        logger.info("No cached rating data available, returning default")
        return {"rating": None, "review_count": None, "source": "cache_miss"}

    async def get_google_rating_fresh(self):
        """Fetch fresh Google rating using Business API - for background task only"""
        try:
            business_api = GoogleBusinessAPI()
            rating_data = await business_api.get_rating_summary()

            logger.info(f"Successfully fetched rating from Business API: {rating_data}")
            return rating_data

        except Exception as e:
            logger.error(f"Error fetching Google rating from Business API: {e}")
            # Return fallback data based on known information
            return {
                "rating": None,
                "review_count": None,
                "source": "api_error",
                "error": str(e)
            }
    async def get_google_reviews(self):
        """Get Google reviews from cache"""
        # Try to get from cache first
        cached_data = await self.get_cached_api_data('google_reviews')
        if cached_data:
            return cached_data

        # If no cache, return empty and let background task handle it
        logger.info("No cached reviews data available, returning empty")
        return {"reviews": [], "total_found": 0, "source": "cache_miss"}

    async def get_google_reviews_fresh(self):
        """Fetch fresh Google reviews using Business API - for background task only"""
        try:
            business_api = GoogleBusinessAPI()
            reviews_data = await business_api.fetch_all_reviews()

            logger.info(f"Successfully fetched {reviews_data.get('total_found', 0)} reviews from Business API")
            return reviews_data

        except Exception as e:
            logger.error(f"Error fetching Google reviews from Business API: {e}")
            return {
                "reviews": [],
                "total_found": 0,
                "source": "api_error",
                "error": str(e)
            }
    # HCP Cache Management Methods
    async def get_hcp_services(self):
        """Get HCP services from cache"""
        # Try to get from cache first
        cached_data = await self.get_cached_api_data('hcp_services')
        if cached_data:
            return cached_data

        # If no cache, return empty and let background task handle it
        logger.info("No cached HCP services data available, returning empty")
        return {"services": [], "source": "cache_miss"}

    async def get_hcp_services_fresh(self):
        """Fetch fresh HCP services - for background task only"""
        try:
            from mayday import hcp
            logger.info("Fetching fresh HCP services...")

            # Get services from HCP integration
            services_data = hcp.get_services()

            if services_data and services_data.get("online_bookable"):
                logger.info(f"Successfully fetched {len(services_data.get('online_bookable', []))} HCP services")
                return {
                    "services": services_data,
                    "source": "hcp_fresh",
                    "total_found": len(services_data.get("online_bookable", []))
                }
            else:
                logger.info("No HCP services data returned (may be due to login timing)")
                return {"services": [], "source": "hcp_empty", "total_found": 0}

        except Exception as e:
            logger.error(f"Error fetching fresh HCP services: {e}")
            return {"services": [], "source": "error", "error": str(e), "total_found": 0}

    # Blog Post Methods
    async def get_blog_posts(self, limit=None, offset=0):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if limit:
                        await cur.execute(
                            "SELECT * FROM blog_posts WHERE published = true ORDER BY created_at DESC LIMIT %s OFFSET %s",
                            (limit, offset)
                        )
                    else:
                        await cur.execute(
                            "SELECT * FROM blog_posts WHERE published = true ORDER BY created_at DESC"
                        )
                    
                    rows = await cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]

    async def get_blog_post(self, post_id):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT * FROM blog_posts WHERE id = %s", (post_id,))
                    row = await cur.fetchone()
                    if row:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, row))
                    return None

    async def create_blog_post(self, title, author, content, image_data=None, image_size='medium'):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO blog_posts (title, author, content, image_data, image_size) 
                           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                        (title, author, content, image_data, image_size)
                    )
                    result = await cur.fetchone()
                    return result[0] if result else None

    async def update_blog_post(self, post_id, title, author, content, image_data=None, image_size='medium'):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """UPDATE blog_posts 
                           SET title = %s, author = %s, content = %s, image_data = %s, image_size = %s, updated_at = CURRENT_TIMESTAMP
                           WHERE id = %s""",
                        (title, author, content, image_data, image_size, post_id)
                    )
                    return cur.rowcount > 0

    async def delete_blog_post(self, post_id):
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("DELETE FROM blog_posts WHERE id = %s", (post_id,))
                    return cur.rowcount > 0

    # Font Management Methods
    async def get_font_settings(self):
        """Get current font settings"""
        font_settings = {
            'heading_font': 'Space Grotesk',
            'body_font': 'Manrope',
            'custom_css': ''
        }

        try:
            async with aiopg.create_pool(self.dsn()) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        await cur.execute("SELECT setting_key, setting_value FROM font_settings WHERE is_active = true")
                        settings = await cur.fetchall()

                        for setting in settings:
                            if setting['setting_key'] in font_settings:
                                font_settings[setting['setting_key']] = setting['setting_value']
        except Exception as e:
            logger.error(f"Error getting font settings: {e}")
            # Return defaults on error

        return font_settings

    async def update_font_settings(self, heading_font, body_font, custom_css=''):
        """Update font settings"""
        async with aiopg.create_pool(self.dsn()) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Update or insert heading font
                    await cur.execute("""
                        INSERT INTO font_settings (setting_key, setting_value)
                        VALUES ('heading_font', %s)
                        ON CONFLICT (setting_key)
                        DO UPDATE SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
                    """, (heading_font, heading_font))

                    # Update or insert body font
                    await cur.execute("""
                        INSERT INTO font_settings (setting_key, setting_value)
                        VALUES ('body_font', %s)
                        ON CONFLICT (setting_key)
                        DO UPDATE SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
                    """, (body_font, body_font))

                    # Update or insert custom CSS
                    await cur.execute("""
                        INSERT INTO font_settings (setting_key, setting_value)
                        VALUES ('custom_css', %s)
                        ON CONFLICT (setting_key)
                        DO UPDATE SET setting_value = %s, updated_at = CURRENT_TIMESTAMP
                    """, (custom_css, custom_css))

    async def reset_font_settings(self):
        """Reset font settings to defaults"""
        await self.update_font_settings(
            heading_font='Space Grotesk',
            body_font='Manrope',
            custom_css=''
        )


class APICacheRefresher:
    def __init__(self, app):
        self.app = app
        self.stop = False
        self.refresh_interval = 300  # Check every 5 minutes

    def shutdown(self):
        self.stop = True

    async def run(self):
        logger.info("API cache refresher started")

        # Initial cache population on startup
        await self.refresh_all_caches()

        while not self.stop:
            try:
                # Check if Google rating cache needs refresh
                if await self.app.data_layer.is_api_cache_expired('google_rating'):
                    logger.info("Google rating cache expired, refreshing...")
                    await self.refresh_rating_cache()

                # Check if Google reviews cache needs refresh
                if await self.app.data_layer.is_api_cache_expired('google_reviews'):
                    logger.info("Google reviews cache expired, refreshing...")
                    await self.refresh_reviews_cache()

                # Check if HCP services cache needs refresh
                if await self.app.data_layer.is_api_cache_expired('hcp_services'):
                    logger.info("HCP services cache expired, refreshing...")
                    await self.refresh_hcp_services_cache()

                await asyncio.sleep(self.refresh_interval)

            except Exception as e:
                logger.error(f"Error in API cache refresher: {e}")
                await asyncio.sleep(self.refresh_interval)  # Continue despite errors

        logger.info("API cache refresher stopped")

    async def refresh_rating_cache(self):
        """Refresh Google rating cache in background"""
        try:
            logger.info("Refreshing Google rating cache...")
            fresh_data = await self.app.data_layer.get_google_rating_fresh()
            if fresh_data and fresh_data.get('rating'):
                await self.app.data_layer.set_cached_api_data('google_rating', fresh_data)
                logger.info(f"Successfully cached rating: {fresh_data.get('rating')} ({fresh_data.get('review_count')} reviews)")
            else:
                logger.warning("Failed to get fresh rating data")
        except Exception as e:
            logger.error(f"Error refreshing rating cache: {e}")

    async def refresh_reviews_cache(self):
        """Refresh Google reviews cache in background"""
        try:
            logger.info("Refreshing Google reviews cache...")
            fresh_data = await self.app.data_layer.get_google_reviews_fresh()
            if fresh_data and fresh_data.get('reviews'):
                await self.app.data_layer.set_cached_api_data('google_reviews', fresh_data)
                logger.info(f"Successfully cached {len(fresh_data.get('reviews', []))} reviews")
            else:
                logger.warning("Failed to get fresh reviews data")
        except Exception as e:
            logger.error(f"Error refreshing reviews cache: {e}")

    async def refresh_hcp_services_cache(self):
        """Refresh HCP services cache in background with retry for login timing"""
        max_retries = 3
        retry_delay = 15  # seconds, slightly longer than HCP login time

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retrying HCP services cache refresh (attempt {attempt + 1}/{max_retries})...")
                else:
                    logger.info("Refreshing HCP services cache...")

                fresh_data = await self.app.data_layer.get_hcp_services_fresh()

                # Check if we got actual services or empty due to login timing
                if fresh_data and fresh_data.get('services') and len(fresh_data.get('services', [])) > 0:
                    # Cache HCP services for only 10 minutes due to AWS S3 signed URL expiration (15 min)
                    await self.app.data_layer.set_cached_api_data('hcp_services', fresh_data, cache_duration_hours=10/60)
                    logger.info(f"Successfully cached {len(fresh_data.get('services', []))} HCP services")
                    return  # Success, exit retry loop

                elif fresh_data and fresh_data.get('source') == 'hcp_empty' and attempt < max_retries - 1:
                    # Empty services likely due to login timing - retry after delay
                    logger.info(f"Got empty HCP services (likely due to login timing), will retry in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    continue

                else:
                    logger.warning("Failed to get fresh HCP services data")
                    break

            except Exception as e:
                logger.error(f"Error refreshing HCP services cache (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Will retry in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Max retries exceeded for HCP services cache refresh")

    async def refresh_all_caches(self):
        """Refresh all caches - used on startup"""
        logger.info("Performing initial cache refresh...")
        await self.refresh_rating_cache()
        await asyncio.sleep(2)  # Small delay between requests
        await self.refresh_reviews_cache()
        await asyncio.sleep(2)  # Small delay between requests
        await self.refresh_hcp_services_cache()

    def start(self):
        asyncio.ensure_future(self.run())


class SessionTracker:
    def __init__(self, app):
        self.app = app
        self.stop = False

    def shutdown(self):
        self.stop = True

    async def run(self):
        logger.info("Session tracker started")
        while not self.stop:
            sessions = await self.app.data_layer.get_sessions()

            for session in sessions:
                await self.app.data_layer.verify_session(
                    session["cookie"],
                    update_ts=False,
                    delete_if_expired=True
                )

            await asyncio.sleep(60) # Check every 60 seconds

        logger.info("Session tracker stopped")

    def start(self):
        asyncio.ensure_future(self.run())