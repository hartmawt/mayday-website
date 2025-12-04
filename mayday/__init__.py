import os
import aiohttp_jinja2
import jinja2
from aiohttp import web

from mayday.housecallpro import HouseCallProIntegration
from mayday.data.data_layer import PostgresDataLayer, SessionTracker, APICacheRefresher
from mayday.logger import logger

hcp = HouseCallProIntegration()


app = web.Application()
app.data_layer = PostgresDataLayer()
app.session_tracker = SessionTracker(app)
app.api_cache_refresher = APICacheRefresher(app)
app.hcp = hcp
aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )
app.add_routes([web.static('/static', os.path.join(os.getcwd(), "static"))])
app.logger = logger


async def init_app():
    from .routes import (
        redirect, get_index, get_blog, get_about, get_admin_login, get_logout,
        post_admin, post_email, post_login, get_google_rating_api, get_google_reviews_api,
        post_image_upload, get_blog_posts_api, post_blog_post_api, delete_blog_post_api,
        get_services_api, post_service_api, get_faqs_api, post_faq_api, initialize_defaults_api,
        post_service_reorder_api, post_faq_reorder_api, post_database_backup_api,
        post_database_restore_api, get_database_backups_api, delete_database_backup_api,
        download_database_backup_api, upload_database_backup_api, get_font_settings_api,
        post_font_settings_api, post_reset_fonts_api
    )

    sections = ["home", "services", "about", "faq", "contact"]

    await app.data_layer.init()
    await app.data_layer.clear_all_sessions()
    app.router.add_get('/', get_index)
    app.router.add_get('/blog', get_blog)
    app.router.add_get('/about', get_about)
    app.router.add_get('/admin-login', get_admin_login)
    app.router.add_get('/logout', get_logout)
    app.router.add_post('/admin', post_admin)
    app.router.add_post('/email', post_email)
    app.router.add_post('/login', post_login)
    app.router.add_get('/api/google-rating', get_google_rating_api)
    app.router.add_get('/api/google-reviews', get_google_reviews_api)
    app.router.add_post('/api/upload-image', post_image_upload)
    app.router.add_get('/api/blog-posts', get_blog_posts_api)
    app.router.add_post('/api/blog-posts', post_blog_post_api)
    app.router.add_delete('/api/blog-posts/{post_id}', delete_blog_post_api)
    app.router.add_get('/api/services', get_services_api)
    app.router.add_post('/api/services', post_service_api)
    app.router.add_get('/api/faqs', get_faqs_api)
    app.router.add_post('/api/faqs', post_faq_api)
    app.router.add_post('/api/initialize-defaults', initialize_defaults_api)
    app.router.add_post('/api/services/reorder', post_service_reorder_api)
    app.router.add_post('/api/faqs/reorder', post_faq_reorder_api)
    app.router.add_post('/api/database/backup', post_database_backup_api)
    app.router.add_post('/api/database/restore', post_database_restore_api)
    app.router.add_get('/api/database/backups', get_database_backups_api)
    app.router.add_delete('/api/database/backup', delete_database_backup_api)
    app.router.add_get('/api/database/backup/{filename}', download_database_backup_api)
    app.router.add_post('/api/database/upload', upload_database_backup_api)
    app.router.add_get('/api/fonts', get_font_settings_api)
    app.router.add_post('/api/fonts', post_font_settings_api)
    app.router.add_post('/api/fonts/reset', post_reset_fonts_api)
    for section in sections:
        app.router.add_get(f'/{section}', redirect)