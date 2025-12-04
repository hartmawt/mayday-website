# Mayday Plumbing - Professional Website & Admin Platform

## Overview

Mayday Plumbing is a modern, professional website for a Virginia-based plumbing company. The platform features a comprehensive admin interface, database backup/restore capabilities, Google Reviews integration, and seamless booking through HouseCall Pro.

## Features

### 🌐 **Public Website**
- **Professional Design**: Modern, responsive layout with trust-building elements
- **Service Showcase**: Dynamic service listings with admin management
- **Google Reviews Integration**: Live review display with automatic updates
- **Contact Forms**: Email integration with customer inquiries
- **Blog System**: Content management with rich text editor
- **Mobile Responsive**: Optimized for all devices

### 🔐 **Admin Dashboard**
- **Website Administrator Management**: Secure user authentication system
- **Content Management**: Edit services, FAQs, blog posts, and page descriptions
- **Database Management**: Complete backup/restore system with upload/download
- **Image Management**: Upload and replace site images (logos, hero backgrounds)
- **Announcement System**: Site-wide notifications and alerts
- **Google Analytics**: Review performance and metrics

### 🛠️ **Technical Features**
- **Async Python Backend**: Built with aiohttp for high performance
- **PostgreSQL Database**: Robust data storage with connection pooling
- **Docker Ready**: Containerized deployment
- **JSON Backup System**: Container-compatible database backups
- **Playwright Integration**: Automated Google Reviews scraping
- **HouseCall Pro API**: Service booking integration

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd mayday_v2
```

### 2. Create Environment File
Copy the sample environment file and configure your settings:
```bash
cp .env.sample .env
```

Edit `.env` with your specific configuration (see Configuration section below).

### 3. Launch with Docker
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

### 4. Access Admin Panel
- Navigate to `/admin-login`
- Default admin credentials are set in your `.env` file
- Or create a new administrator through the admin panel

## Configuration

### Required Environment Variables

Create a `.env` file with the following settings:

```bash
# Database Configuration
POSTGRES_ADMIN_USER=your_db_user
POSTGRES_ADMIN_PASSWORD=your_db_password

# Session Management
SESSION_COOKIE_NAME=MAYDAY
SESSION_TIMEOUT=60

# Email Configuration (for contact forms)
GMAIL_USERNAME=your-email@gmail.com
GMAIL_PASSWORD=your-email-password
MAILER=help@maydayplumbingservice.com

# HouseCall Pro Integration
HOUSECALLPRO_USERNAME=your_hcp_username
HOUSECALLPRO_PASSWORD=your_hcp_password
SERVICE_CATEGORY=pbcat_6a37aed5cdfa46e0b83c3ad4101db1f0
DOMAIN=pro.housecallpro.com
CATEGORY_URI=/alpha/pricebook/categories
SERVICES_URI=/alpha/pricebook/services
CALENDAR_URI=/alpha/scheduling/calendar_items/organization_calendar_items?start_date=%s&end_date=%s
```

## Database Setup

The application automatically initializes the database schema on first run. No manual setup required.

### Default Data
- Sample services and FAQs are automatically created
- Admin user is created from environment variables
- Page descriptions are initialized with default content

## Admin Features

### Website Administrator Management
- Add/remove admin users with secure password hashing
- Role-based access control
- Session management with timeout

### Database Management
- **Create Backup**: Generate JSON backup of entire database
- **Upload Backup**: Restore previously downloaded backup files
- **Download Backup**: Save backups for external storage
- **Restore Database**: Apply backup to current database
- **Delete Backups**: Manage backup storage

### Content Management
- **Services**: Add, edit, reorder, and delete service listings
- **FAQs**: Manage frequently asked questions with search
- **Blog Posts**: Rich text editor with image support
- **Page Content**: Edit hero text, section descriptions, and about page content
- **Images**: Replace logos, hero backgrounds, and about page images

### System Features
- **Announcements**: Site-wide notification system
- **Event Logging**: Track admin actions and system events
- **Google Reviews**: Automatic review fetching and display
- **Session Management**: Secure admin authentication

## Development

### Local Development Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment
cp .env.sample .env

# Run database migrations
python -m mayday.migrations

# Start development server
python -m mayday
```

### Project Structure
```
mayday_v2/
├── mayday/                 # Main application package
│   ├── __init__.py        # Application initialization
│   ├── routes.py          # HTTP route handlers
│   ├── data/              # Data layer and models
│   │   ├── data_layer.py  # Database operations
│   │   ├── schema.json    # Database schema
│   │   └── default_config.py # Default data
│   ├── housecallpro.py    # HouseCall Pro integration
│   ├── mail.py            # Email functionality
│   └── logger.py          # Logging configuration
├── templates/             # Jinja2 HTML templates
├── static/               # CSS, JavaScript, images
├── backups/              # Database backup storage
├── docker-compose.yml    # Container orchestration
├── Dockerfile           # Container configuration
└── requirements.txt     # Python dependencies
```

## Deployment

### Production Deployment
1. **Secure Environment Variables**: Use strong passwords and secure API keys
2. **SSL/TLS**: Configure HTTPS with proper certificates
3. **Database Backups**: Set up automated backup schedule
4. **Monitoring**: Implement health checks and logging
5. **Updates**: Plan for zero-downtime deployments

### Docker Compose Production
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "443:8000"
    environment:
      - POSTGRES_HOST=db
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=maydayplumbing
      - POSTGRES_USER=${POSTGRES_ADMIN_USER}
      - POSTGRES_PASSWORD=${POSTGRES_ADMIN_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## API Documentation

### Public Endpoints
- `GET /` - Homepage
- `GET /about` - About page
- `GET /blog` - Blog listing
- `POST /email` - Contact form submission

### Admin API Endpoints
- `POST /api/database/backup` - Create database backup
- `POST /api/database/upload` - Upload backup file
- `GET /api/database/backup/{filename}` - Download backup
- `POST /api/database/restore` - Restore from backup
- `GET /api/database/backups` - List available backups
- `DELETE /api/database/backup` - Delete backup file

### Content Management API
- `GET /api/services` - List services
- `POST /api/services` - Create/update/delete services
- `GET /api/faqs` - List FAQs
- `POST /api/faqs` - Create/update/delete FAQs
- `GET /api/blog-posts` - List blog posts
- `POST /api/blog-posts` - Create/update blog posts

## Security

### Authentication
- Session-based authentication with secure cookies
- Password hashing using PBKDF2 with SHA-256
- Admin session timeout for security

### Data Protection
- SQL injection prevention with parameterized queries
- File upload validation and size limits
- Secure backup file handling

### Best Practices
- Environment variable configuration
- Error logging without sensitive data exposure
- Input validation and sanitization

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check PostgreSQL container is running
- Verify database credentials in `.env`
- Ensure database host is accessible

**Admin Login Not Working**
- Verify admin credentials in `.env`
- Check session timeout settings
- Clear browser cookies and try again

**Backup/Restore Errors**
- Ensure backups directory has write permissions
- Check file size limits (100MB default)
- Verify backup file format (JSON or SQL)

**Google Reviews Not Loading**
- Check network connectivity
- Verify Google Maps integration
- Check browser console for errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for Mayday Plumbing LLC.

## Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

---

**Mayday Plumbing** - "The Help Behind Every Mayday!"