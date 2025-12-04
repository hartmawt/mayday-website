import os
import time
import json
import datetime
import shutil
import base64
import aiohttp_jinja2
from aiohttp import web

from mayday import app
from mayday.mail import send_mail
from mayday.helpers import fetch_session_cookie
from mayday.recaptcha import verify_recaptcha, get_recaptcha_site_key


SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "MAYDAY")


async def redirect(request, path=None):    
    if path:
        return web.HTTPFound(path)
    else:
        section = request.url.path.strip("/").strip()
        if section:
            return web.HTTPFound(f'/#{section}')
        else:
            return web.HTTPFound('/#home')


@fetch_session_cookie
async def get_blog(request, cookie):
    set_cookie = False
    sessions = {d.pop("cookie"):d for d in await app.data_layer.get_sessions()}
    event, event_type = await app.data_layer.get_event(cookie)
    
    if not cookie or cookie not in sessions:
        cookie = await app.data_layer.create_session()
        set_cookie = True

    # Load blog posts for display
    blog_posts = await app.data_layer.get_blog_posts(limit=5)

    # Load blog header content
    descriptions = await app.data_layer.get_descriptions()

    # Load font settings for server-side application
    font_settings = await app.data_layer.get_font_settings()

    context = {
        "admin": await app.data_layer.verify_session(cookie),
        "blog_posts": blog_posts,
        "descriptions": descriptions,
        "event": event,
        "event_type": event_type,
        "font_settings": font_settings
    }

    response = aiohttp_jinja2.render_template("blog.htm", request, context=context)

    if set_cookie:
        # Only use secure flag for HTTPS connections
        is_secure = request.scheme == 'https'
        response.set_cookie(
            name=SESSION_COOKIE_NAME,
            value=cookie,
            secure=is_secure,
            httponly=True,
            path="/"
        )

    return response


@fetch_session_cookie
async def get_about(request, cookie):
    set_cookie = False
    sessions = {d.pop("cookie"):d for d in await app.data_layer.get_sessions()}
    event, event_type = await app.data_layer.get_event(cookie)
    
    if not cookie or cookie not in sessions:
        cookie = await app.data_layer.create_session()
        set_cookie = True

    # Load descriptions for about page
    descriptions = await app.data_layer.get_descriptions()

    # Load font settings for server-side application
    font_settings = await app.data_layer.get_font_settings()

    context = {
        "admin": await app.data_layer.verify_session(cookie),
        "descriptions": descriptions,
        "event": event,
        "event_type": event_type,
        "font_settings": font_settings
    }

    response = aiohttp_jinja2.render_template("about.htm", request, context=context)

    if set_cookie:
        # Only use secure flag for HTTPS connections
        is_secure = request.scheme == 'https'
        response.set_cookie(
            name=SESSION_COOKIE_NAME,
            value=cookie,
            secure=is_secure,
            httponly=True,
            path="/"
        )

    return response


@fetch_session_cookie
async def get_admin_login(request, cookie):
    set_cookie = False
    sessions = {d.pop("cookie"):d for d in await app.data_layer.get_sessions()}
    event, event_type = await app.data_layer.get_event(cookie)
    
    if not cookie or cookie not in sessions:
        cookie = await app.data_layer.create_session()
        set_cookie = True

    context = {
        "event": event,
        "event_type": event_type,
        "recaptcha_site_key": get_recaptcha_site_key()
    }

    response = aiohttp_jinja2.render_template("admin_login.htm", request, context=context)

    if set_cookie:
        # Only use secure flag for HTTPS connections
        is_secure = request.scheme == 'https'
        response.set_cookie(
            name=SESSION_COOKIE_NAME,
            value=cookie,
            secure=is_secure,
            httponly=True,
            path="/"
        )

    return response


@fetch_session_cookie
async def get_index(request, cookie):
    set_cookie = False
    sessions = {d.pop("cookie"):d for d in await app.data_layer.get_sessions()}
    event, event_type = await app.data_layer.get_event(cookie)

    if not cookie or cookie not in sessions:
        cookie = await app.data_layer.create_session()
        set_cookie = True

    # Load fast operations for immediate page render (now all data loads fast from cache)
    descriptions = await app.data_layer.get_descriptions()
    app.logger.info(f"Page load descriptions: {descriptions}")

    # HCP services are now loaded from cache, no need to ensure login here

    # Load font settings for server-side application
    font_settings = await app.data_layer.get_font_settings()

    context = {
        "meta": await app.data_layer.get_section_meta("all"),
        "website_administrators": await app.data_layer.get_website_administrators(),
        "services": await app.data_layer.get_session_meta_cache(cookie, "services"),
        "admin": await app.data_layer.verify_session(cookie),
        "descriptions": descriptions,
        "announcement": await app.data_layer.get_announcement(),
        "db_services": await app.data_layer.get_services(),
        "db_faqs": await app.data_layer.get_faqs(),
        "available_icons": app.data_layer.get_available_icons(),
        "event": event,
        "event_type": event_type,
        "google_rating": {"rating": None, "review_count": None, "source": "loading"},
        "font_settings": font_settings,
        "recaptcha_site_key": get_recaptcha_site_key()
    }

    response = aiohttp_jinja2.render_template("index.htm", request, context=context)

    if set_cookie:
        # Only use secure flag for HTTPS connections
        is_secure = request.scheme == 'https'
        response.set_cookie(
            name=SESSION_COOKIE_NAME,
            value=cookie,
            secure=is_secure,
            httponly=True,
            path="/"
        )

    return response


@fetch_session_cookie
async def get_google_rating_api(request, cookie):
    """API endpoint to fetch Google rating asynchronously"""
    try:
        google_rating = await app.data_layer.get_google_rating()
        app.logger.info(f"Google rating API: {google_rating}")
        return web.json_response(google_rating)
    except Exception as e:
        app.logger.error(f"Error fetching Google rating: {e}")
        return web.json_response({
            "rating": None, 
            "review_count": None, 
            "source": "error"
        })


@fetch_session_cookie
async def get_google_reviews_api(request, cookie):
    """API endpoint to fetch Google reviews asynchronously"""
    try:
        google_reviews = await app.data_layer.get_google_reviews()
        app.logger.info(f"Google reviews API: Found {len(google_reviews.get('reviews', []))} reviews")
        return web.json_response(google_reviews)
    except Exception as e:
        app.logger.error(f"Error fetching Google reviews: {e}")
        return web.json_response({
            "reviews": [], 
            "total_found": 0,
            "source": "error",
            "error": str(e)
        }, status=500)


@fetch_session_cookie
async def post_image_upload(request, cookie):
    """API endpoint to handle image uploads"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()
    
    try:
        reader = await request.multipart()
        image_key = None
        image_data = None
        filename = None
        
        # Process multipart form data
        while True:
            field = await reader.next()
            if field is None:
                break
                
            if field.name == 'image_key':
                image_key = await field.text()
            elif field.name == 'image' and field.filename:
                filename = field.filename
                image_data = await field.read()
        
        if not image_key or not image_data:
            return web.json_response({'error': 'Missing image key or file'}, status=400)
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = os.path.splitext(filename.lower())[1] if filename else ''
        if file_ext not in allowed_extensions:
            return web.json_response({'error': 'Invalid file type'}, status=400)
        
        # Map image keys to filenames
        image_map = {
            'logo': 'mayday-translucent.png',
            'headshot': 'headshot.jpeg',
            'family': 'family.JPG',
            'benny': 'benny-piece.png',
            'hero': 'hero-bg.jpg',
            'about1': 'headshot.jpeg',  # Fixed: about1 uses headshot.jpeg
            'about2': 'family.JPG',     # Fixed: about2 uses family.JPG
            'about3': 'benny-piece.png' # Fixed: about3 uses benny-piece.png
        }
        
        if image_key not in image_map:
            return web.json_response({'error': 'Invalid image key'}, status=400)
        
        # Save the file
        target_filename = image_map[image_key]
        target_path = os.path.join(os.getcwd(), 'static', 'img', target_filename)
        
        app.logger.info(f"Attempting to save image to: {target_path}")
        app.logger.info(f"Current working directory: {os.getcwd()}")
        app.logger.info(f"File exists before write: {os.path.exists(target_path)}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Create backup of original
        backup_path = target_path + '.backup'
        if os.path.exists(target_path) and not os.path.exists(backup_path):
            shutil.copy2(target_path, backup_path)
            app.logger.info(f"Backup created: {backup_path}")
        
        # Write new image
        try:
            with open(target_path, 'wb') as f:
                f.write(image_data)
            app.logger.info(f"Successfully wrote {len(image_data)} bytes to {target_path}")
            
            # Verify the file was written
            if os.path.exists(target_path):
                file_size = os.path.getsize(target_path)
                app.logger.info(f"File verified: {target_path} (size: {file_size} bytes)")
            else:
                app.logger.error(f"File not found after write: {target_path}")
                
        except Exception as write_error:
            app.logger.error(f"Error writing file: {write_error}")
            raise
        
        await app.data_layer.create_event(
            cookie, 
            f"Image '{image_key}' updated successfully",
            "success"
        )
        
        return web.json_response({
            'success': True,
            'message': f'Image {image_key} updated successfully',
            'filename': target_filename,
            'timestamp': int(time.time() * 1000)  # Add timestamp for cache busting
        })
        
    except Exception as e:
        app.logger.error(f"Error uploading image: {e}")
        await app.data_layer.create_event(
            cookie, 
            f"Failed to update image: {str(e)}",
            "error"
        )
        return web.json_response({'error': 'Upload failed'}, status=500)




@fetch_session_cookie
async def get_logout(request, cookie):
    if cookie:
        await app.data_layer.update_session(cookie, {"admin": False})

    await app.data_layer.create_event(cookie, "Logout successful", "info")
    return web.HTTPFound('/')


@fetch_session_cookie
async def post_admin(request, cookie):
    if await app.data_layer.verify_session(cookie):
        if request.headers.get("Content-Type") == "application/json":
            data = await request.json()
            if data.get("section"):
                # All sections now use the description system
                if data["section"].endswith("-description"):
                    section_name = data["section"].replace("-description", "")
                else:
                    section_name = data["section"]
                descriptions = await app.data_layer.get_descriptions()
                description_text = descriptions.get(section_name, "")
                app.logger.info(f"Loading description for {section_name}: '{description_text}' (available: {list(descriptions.keys())})")
                return web.json_response({"description": description_text})
            
            elif data.get("website-admin"):
                if data["action"] == "delete":
                    await app.data_layer.delete_website_administrator(data["website-admin"])
                    return web.HTTPOk()
                
            else:
                return web.HTTPNotFound()
            
        else:
            data = await request.post()

            if data.get("section-selector"):
                # All sections now use the description system
                if data["section-selector"].endswith("-description"):
                    section_name = data["section-selector"].replace("-description", "")
                else:
                    section_name = data["section-selector"]
                
                await app.data_layer.update_description(
                    section=section_name,
                    text=data.get("description-text", "")
                )
                
                await app.data_layer.create_event(
                    cookie, 
                    f"Updated {section_name.replace('-', ' ').title()}",
                    "success"
                )

            elif data.get("announcement-text") is not None:
                # Handle announcements
                announcement_active = data.get("announcement-active") == "true"
                await app.data_layer.update_announcement(
                    text=data.get("announcement-text", ""),
                    announcement_type=data.get("announcement-type", "info"),
                    active=announcement_active
                )
                
                if data.get("announcement-text", "").strip():
                    await app.data_layer.create_event(
                        cookie, 
                        "Announcement updated successfully",
                        "success"
                    )
                else:
                    await app.data_layer.create_event(
                        cookie, 
                        "Announcement cleared",
                        "info"
                    )

            elif data.get("admin-username"):
                try:
                    # Validate password is provided
                    if not data.get("admin-password"):
                        raise ValueError("Password is required")

                    admin_id = await app.data_layer.create_website_administrator(
                        username=data["admin-username"],
                        email=data["admin-email"],
                        full_name=data["admin-fullname"],
                        password=data["admin-password"]
                    )

                    await app.data_layer.create_event(
                        cookie,
                        f"Website administrator {data['admin-fullname']} added successfully",
                        "success"
                    )
                except ValueError as e:
                    await app.data_layer.create_event(
                        cookie,
                        f"Failed to add administrator: {str(e)}",
                        "error"
                    )

            response = web.HTTPFound('/#admin')
            return response
    else:
        return web.HTTPUnauthorized()


@fetch_session_cookie
async def post_email(request, cookie):
    data = await request.post() or {}

    recaptcha_token = data.get("recaptcha_token")
    client_ip = request.remote

    if not await verify_recaptcha(recaptcha_token, client_ip, expected_action="contact", min_score=0.5):
        await app.data_layer.create_event(
            cookie,
            "Email failed to send: Please complete the reCAPTCHA verification.",
            "error"
        )
        return web.HTTPFound('/')

    result = send_mail(
        customer_email=data["email"],
        name=data["name"],
        message=data["message"]
    )

    await app.data_layer.create_event(cookie, *result)

    return web.HTTPFound('/')


# Blog API Routes
@fetch_session_cookie
async def get_blog_posts_api(request, cookie):
    """Get blog posts with pagination"""
    try:
        limit = int(request.query.get('limit', 10))
        offset = int(request.query.get('offset', 0))
        
        posts = await app.data_layer.get_blog_posts(limit=limit, offset=offset)
        
        # Format posts for frontend
        formatted_posts = []
        for post in posts:
            # Handle backward compatibility - check if image_data exists or fall back to image
            image_data = post.get('image_data') or post.get('image', '')
            
            formatted_posts.append({
                'id': post['id'],
                'title': post['title'],
                'author': post['author'],
                'content': post['content'],
                'image': image_data,
                'imageSize': post['image_size'],
                'date': post['created_at'].strftime('%B %d, %Y') if post['created_at'] else '',
                'published': post['published']
            })
        
        return web.json_response({'posts': formatted_posts})
    except Exception as e:
        app.logger.error(f"Error fetching blog posts: {e}")
        return web.json_response({'error': 'Failed to fetch blog posts'}, status=500)


@fetch_session_cookie
async def post_blog_post_api(request, cookie):
    """Create or update a blog post"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()
    
    try:
        if request.content_type == 'application/json':
            data = await request.json()
        else:
            # Handle multipart form data for image uploads
            reader = await request.multipart()
            data = {}
            image_data = None
            image_filename = None
            
            while True:
                field = await reader.next()
                if field is None:
                    break
                    
                if field.name == 'image' and field.filename:
                    image_filename = field.filename
                    image_data = await field.read()
                else:
                    data[field.name] = await field.text()
        
        # Handle image upload if present - convert to base64
        image_base64 = None
        if image_data and image_filename:
            # Validate file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            file_ext = os.path.splitext(image_filename.lower())[1] if image_filename else ''
            if file_ext not in allowed_extensions:
                return web.json_response({'error': 'Invalid file type'}, status=400)
            
            # Convert to base64 with proper MIME type
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg', 
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(file_ext, 'image/jpeg')
            
            # Create data URL
            base64_data = base64.b64encode(image_data).decode('utf-8')
            image_base64 = f"data:{mime_type};base64,{base64_data}"
        
        # Create or update blog post
        post_id = data.get('id')
        if post_id:
            # Get existing post to preserve image if no new image uploaded
            existing_post = await app.data_layer.get_blog_post(int(post_id))
            # Handle backward compatibility - check both image_data and image fields
            existing_image = existing_post.get('image_data') or existing_post.get('image') if existing_post else None
            existing_image_size = existing_post['image_size'] if existing_post else 'medium'
            
            # Determine which image to use
            final_image = image_base64 or data.get('existing_image') or existing_image
            final_image_size = data.get('imageSize', existing_image_size)
            
            # Update existing post
            success = await app.data_layer.update_blog_post(
                post_id=int(post_id),
                title=data['title'],
                author=data.get('author', 'Mayday Plumbing Team'),
                content=data['content'],
                image_data=final_image,
                image_size=final_image_size
            )
            
            if success:
                await app.data_layer.create_event(cookie, f"Blog post '{data['title']}' updated", "success")
                return web.json_response({'success': True, 'message': 'Blog post updated successfully'})
            else:
                return web.json_response({'error': 'Failed to update blog post'}, status=500)
        else:
            # Create new post
            new_post_id = await app.data_layer.create_blog_post(
                title=data['title'],
                author=data.get('author', 'Mayday Plumbing Team'),
                content=data['content'],
                image_data=image_base64,
                image_size=data.get('imageSize', 'medium')
            )
            
            if new_post_id:
                await app.data_layer.create_event(cookie, f"Blog post '{data['title']}' created", "success")
                return web.json_response({'success': True, 'message': 'Blog post created successfully', 'id': new_post_id})
            else:
                return web.json_response({'error': 'Failed to create blog post'}, status=500)
                
    except Exception as e:
        app.logger.error(f"Error creating/updating blog post: {e}")
        await app.data_layer.create_event(cookie, f"Failed to save blog post: {str(e)}", "error")
        return web.json_response({'error': 'Failed to save blog post'}, status=500)


@fetch_session_cookie
async def delete_blog_post_api(request, cookie):
    """Delete a blog post"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()
    
    try:
        post_id = int(request.match_info['post_id'])
        
        success = await app.data_layer.delete_blog_post(post_id)
        
        if success:
            await app.data_layer.create_event(cookie, f"Blog post deleted", "success")
            return web.json_response({'success': True, 'message': 'Blog post deleted successfully'})
        else:
            return web.json_response({'error': 'Blog post not found'}, status=404)
            
    except Exception as e:
        app.logger.error(f"Error deleting blog post: {e}")
        await app.data_layer.create_event(cookie, f"Failed to delete blog post: {str(e)}", "error")
        return web.json_response({'error': 'Failed to delete blog post'}, status=500)


@fetch_session_cookie
async def post_login(request, cookie):
    data = await request.post() or {}

    recaptcha_token = data.get("recaptcha_token")
    client_ip = request.remote

    if not await verify_recaptcha(recaptcha_token, client_ip, expected_action="login", min_score=0.5):
        await app.data_layer.create_event(
            cookie,
            "Login failed: Please complete the reCAPTCHA verification.",
            "error"
        )
        return web.HTTPFound('/')

    if data.get("username") and data.get("password"):
        try:
            await app.data_layer.create_session(
                cookie=cookie,
                username=data["username"],
                password=data["password"]
            )

            await app.data_layer.create_event(
                cookie,
                "Login successful! Admin utilities are now accessible from the navigation bar.",
                "success"
            )

        except Exception as e:
            app.logger.info(f"{e}")
            await app.data_layer.create_event(
                cookie,
                "Login failed. Please verify your username and password are correct.",
                "error"
            )

    return web.HTTPFound('/')

# Services API endpoints
@fetch_session_cookie
async def get_services_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        services = await app.data_layer.get_services()
        return web.json_response({
            "services": [dict(service) for service in services],
            "available_icons": app.data_layer.get_available_icons()
        })
    else:
        return web.HTTPUnauthorized()

@fetch_session_cookie 
async def post_service_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        data = await request.json()
        
        if data.get('action') == 'create':
            service_id = await app.data_layer.create_service(
                title=data['title'],
                description=data['description'], 
                icon=data['icon'],
                display_order=data.get('display_order', 0)
            )
            return web.json_response({"success": True, "id": service_id})
            
        elif data.get('action') == 'update':
            await app.data_layer.update_service(
                service_id=data['id'],
                title=data['title'],
                description=data['description'],
                icon=data['icon'],
                display_order=data.get('display_order', 0)
            )
            return web.json_response({"success": True})
            
        elif data.get('action') == 'delete':
            await app.data_layer.delete_service(data['id'])
            return web.json_response({"success": True})
            
        else:
            return web.HTTPBadRequest()
    else:
        return web.HTTPUnauthorized()

# Manual initialization endpoint for debugging
@fetch_session_cookie
async def initialize_defaults_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        try:
            await app.data_layer._initialize_default_config()
            return web.json_response({"success": True, "message": "Default configuration initialized"})
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    else:
        return web.HTTPUnauthorized()

# FAQ API endpoints
@fetch_session_cookie
async def get_faqs_api(request, cookie):
    # Allow public access for search, require auth for admin features
    require_auth = request.query.get('admin', 'false').lower() == 'true'
    if require_auth and not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()
    
    # Get parameters
    limit = int(request.query.get('limit', 0))  # 0 means no limit
    offset = int(request.query.get('offset', 0))
    search = request.query.get('search', '').strip()
    
    if search:
        # Search all FAQs
        faqs = await app.data_layer.search_faqs(search, limit=limit if limit > 0 else None, offset=offset)
    else:
        # Regular pagination
        faqs = await app.data_layer.get_faqs(limit=limit if limit > 0 else None, offset=offset)
    
    return web.json_response({"faqs": [dict(faq) for faq in faqs]})

@fetch_session_cookie
async def post_faq_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        data = await request.json()
        
        if data.get('action') == 'create':
            faq_id = await app.data_layer.create_faq(
                question=data['question'],
                answer=data['answer'],
                display_order=data.get('display_order', 0)
            )
            return web.json_response({"success": True, "id": faq_id})
            
        elif data.get('action') == 'update':
            await app.data_layer.update_faq(
                faq_id=data['id'],
                question=data['question'],
                answer=data['answer'],
                display_order=data.get('display_order', 0)
            )
            return web.json_response({"success": True})
            
        elif data.get('action') == 'delete':
            await app.data_layer.delete_faq(data['id'])
            return web.json_response({"success": True})
            
        else:
            return web.HTTPBadRequest()
    else:
        return web.HTTPUnauthorized()

# Reorder API endpoints
@fetch_session_cookie
async def post_service_reorder_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        data = await request.json()
        services = data.get('services', [])
        
        try:
            await app.data_layer.reorder_services(services)
            return web.json_response({"success": True})
        except Exception as e:
            app.logger.error(f"Error reordering services: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)
    else:
        return web.HTTPUnauthorized()

@fetch_session_cookie
async def post_faq_reorder_api(request, cookie):
    if await app.data_layer.verify_session(cookie):
        data = await request.json()
        faqs = data.get('faqs', [])
        
        try:
            await app.data_layer.reorder_faqs(faqs)
            return web.json_response({"success": True})
        except Exception as e:
            app.logger.error(f"Error reordering FAQs: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)
    else:
        return web.HTTPUnauthorized()


# Database backup/restore API endpoints
@fetch_session_cookie
async def post_database_backup_api(request, cookie):
    """Create a database backup"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        result = await app.data_layer.create_database_backup()

        if result["success"]:
            await app.data_layer.create_event(cookie, f"Database backup created: {result['filename']}", "success")
            return web.json_response(result)
        else:
            await app.data_layer.create_event(cookie, f"Database backup failed: {result['error']}", "error")
            return web.json_response(result, status=500)

    except Exception as e:
        app.logger.error(f"Error creating database backup: {e}")
        await app.data_layer.create_event(cookie, f"Database backup error: {str(e)}", "error")
        return web.json_response({"success": False, "error": str(e)}, status=500)


@fetch_session_cookie
async def post_database_restore_api(request, cookie):
    """Restore database from backup"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        data = await request.json()
        backup_filename = data.get('filename')

        if not backup_filename:
            return web.json_response({"success": False, "error": "Backup filename required"}, status=400)

        result = await app.data_layer.restore_database_backup(backup_filename)

        if result["success"]:
            await app.data_layer.create_event(cookie, f"Database restored from: {backup_filename}", "success")
            return web.json_response(result)
        else:
            await app.data_layer.create_event(cookie, f"Database restore failed: {result['error']}", "error")
            return web.json_response(result, status=500)

    except Exception as e:
        app.logger.error(f"Error restoring database: {e}")
        await app.data_layer.create_event(cookie, f"Database restore error: {str(e)}", "error")
        return web.json_response({"success": False, "error": str(e)}, status=500)


@fetch_session_cookie
async def get_database_backups_api(request, cookie):
    """List available database backups"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        result = await app.data_layer.list_database_backups()
        return web.json_response(result)

    except Exception as e:
        app.logger.error(f"Error listing database backups: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


@fetch_session_cookie
async def delete_database_backup_api(request, cookie):
    """Delete a database backup"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        data = await request.json()
        backup_filename = data.get('filename')

        if not backup_filename:
            return web.json_response({"success": False, "error": "Backup filename required"}, status=400)

        result = await app.data_layer.delete_database_backup(backup_filename)

        if result["success"]:
            await app.data_layer.create_event(cookie, f"Database backup deleted: {backup_filename}", "success")
            return web.json_response(result)
        else:
            return web.json_response(result, status=404)

    except Exception as e:
        app.logger.error(f"Error deleting database backup: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


@fetch_session_cookie
async def download_database_backup_api(request, cookie):
    """Download a database backup file"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        backup_filename = request.match_info.get('filename')

        if not backup_filename:
            return web.json_response({"success": False, "error": "Backup filename required"}, status=400)

        backup_path = os.path.join(os.getcwd(), "backups", backup_filename)

        # Security check - ensure filename is valid and file exists
        if not backup_filename.startswith("mayday_backup_") or not (backup_filename.endswith(".json") or backup_filename.endswith(".sql")):
            return web.json_response({"success": False, "error": "Invalid backup filename"}, status=400)

        if not os.path.exists(backup_path):
            return web.json_response({"success": False, "error": "Backup file not found"}, status=404)

        # Determine content type
        content_type = "application/json" if backup_filename.endswith(".json") else "application/sql"

        # Create response with file content
        response = web.FileResponse(
            backup_path,
            headers={
                'Content-Disposition': f'attachment; filename="{backup_filename}"',
                'Content-Type': content_type
            }
        )

        # Log the download
        await app.data_layer.create_event(cookie, f"Database backup downloaded: {backup_filename}", "info")

        return response

    except Exception as e:
        app.logger.error(f"Error downloading database backup: {e}")
        return web.json_response({"success": False, "error": str(e)}, status=500)


@fetch_session_cookie
async def upload_database_backup_api(request, cookie):
    """Upload a database backup file"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        reader = await request.multipart()
        backup_file = None
        original_filename = None

        # Process multipart form data
        while True:
            field = await reader.next()
            if field is None:
                break

            if field.name == 'backup_file' and field.filename:
                original_filename = field.filename
                backup_file = await field.read()
                break

        if not backup_file or not original_filename:
            return web.json_response({'error': 'No backup file provided'}, status=400)

        # Validate file extension
        if not (original_filename.endswith('.json') or original_filename.endswith('.sql')):
            return web.json_response({'error': 'Invalid file type. Only .json and .sql files are allowed.'}, status=400)

        # Generate new filename with timestamp to avoid conflicts
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = '.json' if original_filename.endswith('.json') else '.sql'
        new_filename = f"mayday_backup_uploaded_{timestamp}{file_extension}"

        # Save to backups directory
        backups_dir = os.path.join(os.getcwd(), "backups")
        os.makedirs(backups_dir, exist_ok=True)

        backup_path = os.path.join(backups_dir, new_filename)

        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(backup_file) > max_size:
            return web.json_response({'error': 'File too large. Maximum size is 100MB.'}, status=400)

        # For JSON files, validate the structure
        if file_extension == '.json':
            try:
                backup_data = json.loads(backup_file.decode('utf-8'))

                # Basic validation of backup structure
                if not isinstance(backup_data, dict) or 'tables' not in backup_data:
                    return web.json_response({'error': 'Invalid backup file format. Missing required structure.'}, status=400)

                # Re-encode for consistent formatting
                backup_file = json.dumps(backup_data, indent=2, ensure_ascii=False).encode('utf-8')

            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return web.json_response({'error': f'Invalid JSON file: {str(e)}'}, status=400)

        # Write the file
        with open(backup_path, 'wb') as f:
            f.write(backup_file)

        file_size = os.path.getsize(backup_path)

        app.logger.info(f"Backup file uploaded: {new_filename} ({file_size} bytes)")
        await app.data_layer.create_event(
            cookie,
            f"Database backup uploaded: {new_filename} (original: {original_filename})",
            "success"
        )

        return web.json_response({
            'success': True,
            'message': 'Backup file uploaded successfully',
            'filename': new_filename,
            'original_filename': original_filename,
            'size': file_size
        })

    except Exception as e:
        app.logger.error(f"Error uploading backup file: {e}")
        await app.data_layer.create_event(
            cookie,
            f"Failed to upload backup file: {str(e)}",
            "error"
        )
        return web.json_response({'error': f'Upload failed: {str(e)}'}, status=500)


# Font Management API endpoints
@fetch_session_cookie
async def get_font_settings_api(request, cookie):
    """Get current font settings"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        font_settings = await app.data_layer.get_font_settings()
        return web.json_response({
            'success': True,
            'settings': font_settings
        })
    except Exception as e:
        app.logger.error(f"Error getting font settings: {e}")
        return web.json_response({'error': 'Failed to get font settings'}, status=500)


@fetch_session_cookie
async def post_font_settings_api(request, cookie):
    """Update font settings"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        data = await request.json()

        heading_font = data.get('heading_font', '').strip()
        body_font = data.get('body_font', '').strip()
        custom_css = data.get('custom_css', '').strip()

        if not heading_font or not body_font:
            return web.json_response({'error': 'Both heading and body fonts are required'}, status=400)

        # Save font settings to data layer
        await app.data_layer.update_font_settings(
            heading_font=heading_font,
            body_font=body_font,
            custom_css=custom_css
        )

        await app.data_layer.create_event(
            cookie,
            f"Font settings updated - Headings: {heading_font}, Body: {body_font}",
            "success"
        )

        return web.json_response({
            'success': True,
            'message': 'Font settings updated successfully'
        })

    except Exception as e:
        app.logger.error(f"Error updating font settings: {e}")
        await app.data_layer.create_event(
            cookie,
            f"Failed to update font settings: {str(e)}",
            "error"
        )
        return web.json_response({'error': 'Failed to update font settings'}, status=500)


@fetch_session_cookie
async def post_reset_fonts_api(request, cookie):
    """Reset fonts to default"""
    if not await app.data_layer.verify_session(cookie):
        return web.HTTPUnauthorized()

    try:
        # Reset to default fonts
        await app.data_layer.update_font_settings(
            heading_font='Space Grotesk',
            body_font='Manrope',
            custom_css=''
        )

        await app.data_layer.create_event(
            cookie,
            "Font settings reset to default",
            "success"
        )

        return web.json_response({
            'success': True,
            'message': 'Fonts reset to default successfully'
        })

    except Exception as e:
        app.logger.error(f"Error resetting fonts: {e}")
        await app.data_layer.create_event(
            cookie,
            f"Failed to reset fonts: {str(e)}",
            "error"
        )
        return web.json_response({'error': 'Failed to reset fonts'}, status=500)

