# Traefik + Let's Encrypt Setup Guide

This setup provides automatic HTTPS certificate management using Traefik reverse proxy with Let's Encrypt HTTP challenge.

## Prerequisites

1. **Domain Name**: You need a domain name pointed to your server's public IP
2. **Open Ports**: Ports 80 and 443 must be accessible from the internet
3. **Amazon Lightsail**: Ensure your firewall allows HTTP (80) and HTTPS (443) traffic

## Setup Steps

### 1. Configure Environment Variables

1. Copy the variables from `traefik-env.sample` to your `.env` file:
   ```bash
   cat traefik-env.sample >> .env
   ```

2. Update the following variables in your `.env` file:

   **Required:**
   - `DOMAIN`: Your domain name (e.g., `example.com`)

   **Optional:**
   - `TRAEFIK_AUTH_USERS`: Basic auth for Traefik dashboard access

### 2. Configure DNS

1. Point your domain's A record to your Amazon Lightsail instance's public IP
2. If you want the Traefik dashboard, also create an A record for `traefik-dashboard.yourdomain.com`
3. Wait for DNS propagation (usually 5-15 minutes)

### 3. Generate Traefik Dashboard Password (Optional)

If you want to access the Traefik dashboard:

```bash
# Install htpasswd (if not available)
# Ubuntu/Debian: sudo apt-get install apache2-utils
# macOS: brew install httpd

# Generate password hash (replace 'admin' and 'your-password')
echo $(htpasswd -nb admin your-password) | sed -e s/\\$/\\$\\$/g
```

Add the output to your `.env` file as `TRAEFIK_AUTH_USERS`.

### 4. Configure Amazon Lightsail Firewall

1. In your Lightsail console, go to your instance
2. Click the "Networking" tab
3. Ensure these ports are open:
   - **HTTP**: Port 80 (TCP)
   - **HTTPS**: Port 443 (TCP)
   - **SSH**: Port 22 (TCP) - if you need SSH access

### 5. Update Traefik Configuration

Edit `data/traefik.yml` and update:
- Line 26: Replace `your-email@example.com` with your actual email address

### 6. Start the Services

```bash
docker-compose up -d
```

### 7. Verify Setup

1. **Check containers are running:**
   ```bash
   docker-compose ps
   ```

2. **Check Traefik logs:**
   ```bash
   docker-compose logs traefik
   ```

3. **Access your application:**
   - Your app: `https://yourdomain.com`
   - Traefik dashboard: `https://traefik-dashboard.yourdomain.com` (if configured)

## SSL Certificate Management

- **Automatic renewal**: Certificates renew automatically before expiration
- **Certificate storage**: Stored in `data/acme.json` (do not delete this file)
- **HTTP challenge**: Uses HTTP validation on port 80 (requires public internet access)

## Troubleshooting

### Certificate Issues

1. **Check Traefik logs:**
   ```bash
   docker-compose logs traefik | grep -i error
   ```

2. **Verify DNS and network settings:**
   - Domain A record points to your server's public IP
   - Ports 80 and 443 are accessible from the internet
   - Amazon Lightsail firewall allows HTTP/HTTPS traffic

3. **Test staging environment first:**
   - In `data/traefik.yml`, uncomment the staging server line (line 30)
   - Comment out the production server line (line 29)
   - Restart Traefik: `docker-compose restart traefik`

### Domain Access Issues

1. **Verify DNS resolution:**
   ```bash
   nslookup yourdomain.com
   ```

2. **Check firewall:**
   - Ensure ports 80 and 443 are open
   - Ensure ports 80 and 443 are not used by other services

3. **Verify domain configuration:**
   - Check your `.env` file has the correct `DOMAIN` value
   - Ensure DNS A records point to your server IP

### Container Issues

1. **Check all containers are running:**
   ```bash
   docker-compose ps
   ```

2. **Restart services:**
   ```bash
   docker-compose restart
   ```

3. **Rebuild if needed:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Security Notes

- The `data/acme.json` file contains your certificates and private keys
- Keep `data/acme.json` backed up but secure (600 permissions)
- Never commit your `.env` file to version control
- Consider using secrets management for production deployments

## File Structure

```
.
├── docker-compose.yml          # Updated with Traefik service
├── data/
│   ├── traefik.yml            # Main Traefik configuration
│   ├── config.yml             # Additional middleware configuration
│   └── acme.json              # Let's Encrypt certificates (auto-generated)
├── traefik-env.sample         # Environment variables template
└── TRAEFIK_SETUP.md          # This setup guide
```