# E-Mining University Platform

A comprehensive Django-based learning management system (LMS) designed specifically for mining education and professional development. This platform enables students to enroll in mining courses, track their progress, interact with instructors, and earn certificates upon completion.

![Django](https://img.shields.io/badge/Django-6.0-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

### Core Learning Management
- **Course Catalog**: Browse and search mining courses with filtering by category, level, and price
- **Video Learning**: Integrated YouTube video player for course content
- **Progress Tracking**: Real-time course completion tracking and analytics
- **Discussion Forums**: Course-specific discussions for student-instructor interaction
- **Certificates**: Automatic certificate generation upon course completion
- **Reviews & Ratings**: Student reviews and ratings system for courses

### User Management
- **Student Registration**: Secure user registration and authentication
- **Instructor Profiles**: Comprehensive instructor profiles with bio and course history
- **User Profiles**: Extended user profiles with personal information and preferences
- **Dashboard**: Personalized learning dashboard with progress overview

### E-Commerce Integration
- **Shopping Cart**: Add multiple courses to cart before purchase
- **Payment Processing**: Secure payment integration with Paystack
- **Order Management**: Complete order tracking and history
- **Enrollment Management**: Automatic enrollment after successful payment

### Content Management
- **Course Creation**: Full-featured course creation with sections and lessons
- **File Uploads**: Support for course materials and resources
- **Course Structure**: Organized content with sections, lessons, and materials
- **Media Support**: Image uploads for course thumbnails and user profiles

## 🏗️ Technology Stack

### Backend
- **Framework**: Django 6.0+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Django's built-in authentication system
- **Payment**: Paystack API integration
- **Email**: SMTP email delivery

### Frontend
- **Templates**: Django templates with Bootstrap 5
- **Forms**: Django Crispy Forms with Bootstrap 5
- **JavaScript**: Vanilla JavaScript for interactive features
- **CSS**: Bootstrap 5 + custom CSS

### Production Infrastructure
- **Web Server**: Gunicorn
- **Reverse Proxy**: Nginx
- **Cache**: Redis
- **Static Files**: WhiteNoise (with CDN support)
- **File Storage**: AWS S3 (configurable)
- **Error Tracking**: Sentry integration

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12 or higher
- PostgreSQL 14+ (for production)
- Redis 6+ (for caching)
- Git
- pip or uv (Python package manager)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/emining-university.git
cd emining-university
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Using uv (recommended)
uv pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:

```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,emining.digitalrepublic.space
CSRF_TRUSTED_ORIGINS=https://emining.digitalrepublic.space

# Database Configuration (PostgreSQL for production)
DB_NAME=emining_db
DB_USER=emining_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
CONTACT_EMAIL=contact@yourdomain.com

# Payment Configuration (Paystack)
PAYSTACK_SECRET_KEY=sk_test_your-secret-key
PAYSTACK_PUBLIC_KEY=pk_test_your-public-key

# Site Configuration
SITE_URL=http://localhost:8000

# Cache Configuration (Redis)
REDIS_URL=redis://127.0.0.1:6379/1
```

### 5. Database Setup
```bash
# Create database (PostgreSQL)
createdb emining_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 7. Load Sample Data (Optional)
```bash
# Load sample courses and categories
python manage.py import_courses
```

### 8. Start Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 🔧 Development Setup

### Database Configuration
For development, you can use SQLite (default):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

For PostgreSQL development:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'emining_dev',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Development Dependencies
Uncomment development dependencies in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
python manage.py test
```

### Code Formatting
```bash
# Using black
black .

# Using isort
isort .
```

## 🚀 Production Deployment

### Environment Variables
Set these environment variables for production:

```bash
# Security
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=emining.digitalrepublic.space,www.emining.digitalrepublic.space
CSRF_TRUSTED_ORIGINS=https://emining.digitalrepublic.space

# Database
DB_NAME=emining_prod
DB_USER=emining_user
DB_PASSWORD=secure-production-password
DB_HOST=your-db-host
DB_PORT=5432

# Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### Web Server Configuration (Nginx)
```nginx
server {
    listen 80;
    server_name emining.digitalrepublic.space www.emining.digitalrepublic.space;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name emining.digitalrepublic.space www.emining.digitalrepublic.space;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /static/ {
        alias /path/to/emining-university/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/emining-university/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service (Gunicorn)
Create `/etc/systemd/system/emining.service`:
```ini
[Unit]
Description=Emining University Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/emining-university
Environment="PATH=/path/to/emining-university/.venv/bin"
ExecStart=/path/to/emining-university/.venv/bin/gunicorn --workers 3 --bind unix:/path/to/emining-university/emining.sock emining_university.wsgi:application

[Install]
WantedBy=multi-user.target
```

## 📁 Project Structure

```
emining-university/
├── courses/                     # Main application
│   ├── admin.py                # Django admin configuration
│   ├── forms.py                # Form classes
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── urls.py                 # URL routing
│   ├── utils.py                # Utility functions
│   ├── management/
│   │   └── commands/           # Custom management commands
│   ├── migrations/             # Database migrations
│   └── tests.py               # Test suite
├── emining_university/         # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Homepage
│   ├── courses/               # Course-related templates
│   ├── registration/          # Authentication templates
│   ├── cart/                  # Shopping cart templates
│   └── certificates/          # Certificate templates
├── static/                     # Static files
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Image assets
├── media/                      # User-uploaded files
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── production_readiness_report.md  # Production assessment
└── README.md                  # This file
```

## 🎓 Usage Guide

### For Students
1. **Registration**: Create an account with email verification
2. **Browse Courses**: Explore available mining courses
3. **Enroll**: Add courses to cart and complete payment
4. **Learn**: Access video content and course materials
5. **Track Progress**: Monitor completion percentage
6. **Discuss**: Participate in course discussions
7. **Review**: Rate and review completed courses
8. **Certificate**: Download certificates upon completion

### For Instructors
1. **Profile Setup**: Complete instructor profile
2. **Course Creation**: Create courses with sections and lessons
3. **Content Management**: Upload videos and materials
4. **Student Interaction**: Respond to discussions
5. **Progress Monitoring**: Track student progress
6. **Certificate Management**: Issue completion certificates

### For Administrators
1. **User Management**: Manage users and instructors
2. **Course Oversight**: Monitor all courses and content
3. **Financial Reports**: Track payments and revenue
4. **System Configuration**: Configure platform settings

## 🔒 Security Considerations

### Authentication
- Django's built-in authentication with password hashing
- Session management with secure cookies
- CSRF protection enabled
- Rate limiting on authentication endpoints

### Data Protection
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection with Django templates
- File upload restrictions and validation

### Payment Security
- Secure payment processing with Paystack
- Webhook signature verification
- PCI DSS compliance through payment processor
- Order validation and fraud prevention

## 📊 Performance Optimization

### Database
- Optimized queries with `select_related` and `prefetch_related`
- Database indexing on frequently queried fields
- Connection pooling for production

### Caching
- Redis-based caching for frequently accessed data
- Template fragment caching
- Static files caching with WhiteNoise

### Static Files
- Compressed static files with WhiteNoise
- CDN support for media files
- Optimized image handling

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test courses

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage
- Model tests
- View tests
- Form tests
- Integration tests
- Payment flow tests

## 📈 Monitoring & Maintenance

### Logging
- Structured logging with configurable levels
- Error tracking with Sentry integration
- Performance monitoring setup

### Backup Strategy
- Database backups with pg_dump
- Media files backup to cloud storage
- Configuration files version control

### Health Checks
- Database connectivity monitoring
- External service (Paystack, email) health checks
- Performance metrics tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use semantic commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Production Deployment Guide](production_readiness_report.md)
- [API Documentation](docs/api.md)

### Community
- Issues: [GitHub Issues](https://github.com/yourusername/emining-university/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/emining-university/discussions)

### Professional Support
For enterprise support and customization, contact: support@eminingcampus.com

## 🗺️ Roadmap

### Version 1.1
- [ ] Mobile responsive improvements
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] API documentation

### Version 1.2
- [ ] Mobile app development
- [ ] Advanced reporting features
- [ ] Integration with external LMS systems
- [ ] Bulk course import/export

### Version 2.0
- [ ] Microlearning modules
- [ ] AI-powered recommendations
- [ ] Virtual reality content support
- [ ] Advanced proctoring system

## 📝 Changelog

### v1.0.0 (Current)
- Initial release
- Core LMS functionality
- Paystack payment integration
- Course creation and management
- Student progress tracking
- Certificate generation

---

**Built with ❤️ for the mining education community**

*Empowering mining professionals through quality education and continuous learning.*