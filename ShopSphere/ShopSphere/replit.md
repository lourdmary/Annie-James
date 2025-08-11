# Overview

Fashion Store is a complete e-commerce web application built with Flask that provides a comprehensive online shopping experience. The application features user authentication with OTP verification, product catalog management, shopping cart functionality, order processing, wishlist management, and a robust admin panel. It supports multiple user types including customers and administrators with different access levels, implements a loyalty points system, and includes membership tiers with benefits.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Theme**: Dark theme implementation using Bootstrap's dark mode
- **JavaScript**: Vanilla JavaScript for interactive features like cart management, search, and form validations
- **CSS Framework**: Custom CSS built on top of Bootstrap with Fashion Store branding

## Backend Architecture
- **Framework**: Flask web framework with modular route handling
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Authentication**: Flask-Login for session management with user role-based access control
- **Security**: Password hashing with Werkzeug, session management, and CSRF protection
- **Application Structure**: 
  - `app.py` - Main application factory and configuration
  - `routes.py` - URL route handlers and business logic
  - `models.py` - Database models and relationships
  - `utils.py` - Utility functions for email, calculations, and helpers

## Database Schema Design
- **User Management**: Comprehensive user profiles with authentication, membership tiers, and loyalty points
- **Product Catalog**: Products with categories, inventory tracking, pricing, and discount support
- **Order Management**: Full order lifecycle with items, payment tracking, and status management
- **Shopping Features**: Shopping cart, wishlist, and product interaction (likes, comments)
- **Admin System**: Role-based admin access with different permission levels
- **Communication**: OTP verification system for secure operations

## Authentication & Authorization
- **Multi-tier Access Control**: Users, limited admins, and super admins with different capabilities
- **OTP Verification**: Email-based OTP for registration and password reset
- **Session Management**: Flask-Login handles user sessions and authentication state
- **Security Features**: Password hashing, session secrets, and form validation

## Business Logic Features
- **Loyalty Program**: Points-based system with membership tier progression (Bronze, Silver, Gold, Platinum)
- **Discount System**: Flexible discount codes with percentage/fixed amount options
- **Inventory Management**: Stock tracking with size-based inventory
- **Order Processing**: Complete order workflow with payment method support
- **Admin Analytics**: Dashboard with revenue, order, and customer analytics

# External Dependencies

## Email Service Integration
- **Brevo API**: Third-party email service for OTP delivery and transactional emails
- **Configuration**: API key-based authentication with environment variable management

## Database Options
- **Development**: SQLite for local development and testing
- **Production**: Configurable via DATABASE_URL environment variable for PostgreSQL or other databases
- **Connection Management**: Pool recycling and pre-ping for connection reliability

## Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for consistent iconography throughout the application
- **Chart.js**: Analytics dashboard visualization (referenced in admin templates)

## Development Tools
- **Flask Extensions**: SQLAlchemy for ORM, Flask-Login for authentication
- **Security Middleware**: ProxyFix for handling proxy headers in deployment
- **Environment Management**: Environment variable configuration for secrets and API keys

## Payment Integration Ready
- **UPI Support**: Basic UPI payment information display
- **Cash on Delivery**: COD payment option with city-based delivery
- **Extensible**: Architecture supports adding payment gateway integrations