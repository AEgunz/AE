# PUBG Mobile Tournament Website - Deployment Instructions

## Overview
This document provides instructions for deploying the PUBG Mobile Tournament website on a Hostinger VPS server with MySQL database support.

## Prerequisites
- A Hostinger VPS server with root access
- MySQL database server installed
- Domain name configured to point to your VPS (optional but recommended)
- Basic knowledge of Linux commands and server management

## Files Structure
The project has the following structure:
```
pubg_tournament/
├── venv/                  # Virtual environment (not included in deployment)
├── src/                   # Source code
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   ├── static/            # Static files (HTML, CSS, JS, images)
│   └── main.py            # Main application entry point
└── requirements.txt       # Python dependencies
```

## Deployment Steps

### 1. Server Preparation

1. Connect to your Hostinger VPS via SSH:
   ```
   ssh username@your_server_ip
   ```

2. Update the system:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

3. Install required packages:
   ```
   sudo apt install -y python3-pip python3-venv nginx mysql-client
   ```

### 2. Database Setup

1. Connect to your MySQL server:
   ```
   mysql -u root -p
   ```

2. Create a new database and user:
   ```sql
   CREATE DATABASE pubg_tournament;
   CREATE USER 'pubg_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON pubg_tournament.* TO 'pubg_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

### 3. Application Deployment

1. Create a directory for the application:
   ```
   sudo mkdir -p /var/www/pubg_tournament
   ```

2. Copy the application files to the server:
   ```
   # If using SCP from your local machine:
   scp -r pubg_tournament/* username@your_server_ip:/var/www/pubg_tournament/
   ```

3. Set proper permissions:
   ```
   sudo chown -R www-data:www-data /var/www/pubg_tournament
   ```

4. Create and activate a virtual environment:
   ```
   cd /var/www/pubg_tournament
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### 4. Configure Environment Variables

1. Create an environment file:
   ```
   sudo nano /var/www/pubg_tournament/.env
   ```

2. Add the following environment variables:
   ```
   DB_USERNAME=pubg_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=pubg_tournament
   ```

### 5. Configure Gunicorn

1. Install Gunicorn:
   ```
   pip install gunicorn
   ```

2. Create a Gunicorn service file:
   ```
   sudo nano /etc/systemd/system/pubg_tournament.service
   ```

3. Add the following content:
   ```
   [Unit]
   Description=Gunicorn instance to serve PUBG Tournament
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/pubg_tournament
   Environment="PATH=/var/www/pubg_tournament/venv/bin"
   EnvironmentFile=/var/www/pubg_tournament/.env
   ExecStart=/var/www/pubg_tournament/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --chdir src main:app

   [Install]
   WantedBy=multi-user.target
   ```

4. Enable and start the service:
   ```
   sudo systemctl enable pubg_tournament
   sudo systemctl start pubg_tournament
   ```

### 6. Configure Nginx

1. Create an Nginx configuration file:
   ```
   sudo nano /etc/nginx/sites-available/pubg_tournament
   ```

2. Add the following content:
   ```
   server {
       listen 80;
       server_name your_domain.com;  # Replace with your domain or server IP

       location / {
           include proxy_params;
           proxy_pass http://127.0.0.1:5000;
       }

       location /static {
           alias /var/www/pubg_tournament/src/static;
       }

       location /uploads {
           alias /var/www/pubg_tournament/src/static/uploads;
       }
   }
   ```

3. Enable the site:
   ```
   sudo ln -s /etc/nginx/sites-available/pubg_tournament /etc/nginx/sites-enabled
   ```

4. Test Nginx configuration:
   ```
   sudo nginx -t
   ```

5. Restart Nginx:
   ```
   sudo systemctl restart nginx
   ```

### 7. Set Up SSL (Optional but Recommended)

1. Install Certbot:
   ```
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. Obtain SSL certificate:
   ```
   sudo certbot --nginx -d your_domain.com
   ```

3. Follow the prompts to complete the SSL setup.

### 8. Create Upload Directories

1. Create directories for uploads:
   ```
   sudo mkdir -p /var/www/pubg_tournament/src/static/uploads/logos
   sudo chown -R www-data:www-data /var/www/pubg_tournament/src/static/uploads
   ```

### 9. Initial Admin Setup

1. Connect to your MySQL database:
   ```
   mysql -u pubg_user -p pubg_tournament
   ```

2. Create an admin user:
   ```sql
   INSERT INTO users (username, password, email, is_admin) 
   VALUES ('admin', 'your_secure_password', 'admin@example.com', 1);
   EXIT;
   ```

### 10. Verify Deployment

1. Access your website at `http://your_domain.com` or `https://your_domain.com` if SSL is configured.
2. Access the admin panel at `http://your_domain.com/admin.html`
3. Log in with the admin credentials you created.

## Troubleshooting

### Check Application Logs
```
sudo journalctl -u pubg_tournament
```

### Check Nginx Logs
```
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart Services
```
sudo systemctl restart pubg_tournament
sudo systemctl restart nginx
```

## Maintenance

### Updating the Application

1. Pull the latest changes:
   ```
   cd /var/www/pubg_tournament
   # Update files as needed
   ```

2. Install any new dependencies:
   ```
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Restart the service:
   ```
   sudo systemctl restart pubg_tournament
   ```

### Database Backup

1. Create a backup of the database:
   ```
   mysqldump -u pubg_user -p pubg_tournament > backup_$(date +%Y%m%d).sql
   ```

## Security Considerations

1. Use strong passwords for all accounts
2. Keep the server updated with security patches
3. Consider implementing a firewall (e.g., UFW)
4. Regularly backup your database and application files
5. Implement proper password hashing in the application (currently using plaintext for simplicity)

## Support

For any issues or questions, please contact the development team.
