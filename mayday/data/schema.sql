-- Database schema for Mayday Plumbing application

-- Services table for configurable "Our Services" section
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(100) NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FAQ table for configurable FAQ section
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Website administrators table for site management
CREATE TABLE IF NOT EXISTS website_administrators (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Partial unique indexes to allow duplicates for inactive users
CREATE UNIQUE INDEX IF NOT EXISTS website_administrators_username_active_unique
ON website_administrators (LOWER(username)) WHERE is_active = true;

CREATE UNIQUE INDEX IF NOT EXISTS website_administrators_email_active_unique
ON website_administrators (LOWER(email)) WHERE is_active = true;

-- Existing tables (for reference)
-- descriptions table already exists
-- sessions table already exists
-- events table already exists
-- blog_posts table already exists

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_services_active_order ON services(is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_faqs_active_order ON faqs(is_active, display_order);