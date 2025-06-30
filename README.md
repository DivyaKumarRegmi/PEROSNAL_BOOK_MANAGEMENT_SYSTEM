# PEROSNAL_BOOK_MANAGEMENT_SYSTEM
A Django-based personal book manager with user registration, email verification, password reset, and CRUD operations. Supports both session and JWT authentication via REST API. Uses MySQL for the database and Brevo SMTP for sending verification and reset emails.
This project serves as a powerful demonstration of integrating a standard Django application with an external Identity and Access Management (IAM) solution like Keycloak. It features a dual-authentication system, fine-grained role-based access control (RBAC), a complete RESTful API, and a production-ready containerized setup.
Key Features
1. Core Functionality
Complete Book Management: Full CRUD (Create, Read, Update, Delete) functionality for managing book records. Each book is securely associated with the user who created it.
User-Centric Design: Users can view a list of books they have personally added to the system.
2. Advanced Authentication & Authorization
Dual Authentication System: Offers flexible user authentication through two distinct methods, allowing the system to function as a standalone service or as part of a larger SSO ecosystem.
Traditional Django Authentication: Includes secure user registration with email verification, a full password reset flow, and standard username/password login.
Keycloak Single Sign-On (OIDC): Seamlessly integrates with Keycloak for enterprise-grade authentication using the OpenID Connect (OIDC) Authorization Code Flow.
Advanced Role-Based Access Control (RBAC): Implements a sophisticated authorization layer powered by roles defined and managed in Keycloak.
Protected Views & API Endpoints: Access to critical operations (like creating, updating, or deleting books) is restricted to users with specific roles (e.g., librarian).
Consistent Permissions: Utilizes custom Django decorators for web views and DRF Permission Classes for the API, ensuring uniform security rules across the entire application.
Single Sign-Out (SSO): Features a "smart" logout mechanism that correctly terminates both the local Django session and the remote Keycloak session, ensuring a complete and secure sign-out process for OIDC users.
3. RESTful API
Comprehensive API: Provides a full-featured RESTful API built with Django REST Framework for programmatic access to book and user data.
JWT Authentication: The API is secured using JSON Web Tokens (JWT) for stateless, token-based authentication, suitable for use with modern frontend frameworks (like React, Vue, or Angular) or mobile applications.
Token Blacklisting: Implements a secure API logout by blacklisting refresh tokens, preventing their reuse after a user has logged out.
User Profile Endpoint: Authenticated users can view and update their profile information through a dedicated API endpoint.
4. Deployment & Architecture
Containerized with Docker: The entire application stack (Django, Keycloak, MySQL) is containerized using Docker and Docker Compose, ensuring consistent, reproducible deployments and simplifying the development setup.
Secure Configuration: Manages sensitive information and environment-specific settings (like SECRET_KEY, database credentials, and OIDC client details) using a .env file and the python-decouple library, adhering to the best practice of never hardcoding secrets in the source code.
Internal & Public Networking: The configuration correctly distinguishes between internal Docker network hostnames (for server-to-server communication) and public-facing domains (for browser redirects), a critical aspect of containerized web deployments.
Technology Stack
Backend: Django, Django REST Framework
Authentication: Keycloak (OIDC), mozilla-django-oidc, rest_framework_simplejwt
Database: MySQL
Containerization: Docker, Docker Compose
Configuration: python-decouple
System Architecture
The system is designed with a clear separation of concerns, enabling scalability and security.

Getting Started
Follow these instructions to get the project running on your local machine for development and testing purposes.

Prerequisites
Docker
Docker Compose
Installation
Clone the repository:
git clone https://github.com/your-username/personal-book-management-system.git
cd personal-book-management-system

Create the environment file: Create a .env file in the project root by copying the example.
cp .env.example .env

Build and run the containers: Use Docker Compose to build the images and start the services.
docker-compose up --build

Apply database migrations: In a separate terminal, once the containers are running, execute the database migrations.
docker-compose exec backend python manage.py migrate

Access the application:

Django Application: http://localhost:8000
Keycloak Admin Console: http://localhost:8080 (Use the admin credentials from your .env file).
Keycloak Configuration
For the OIDC integration to work, you need to perform a one-time setup in your Keycloak instance:

Create a new realm (e.g., my-app-realm).
Create a new client with the Client ID django-app.
Set Access Type to confidential.
Add http://localhost:8000/* to the Valid Redirect URIs.
Add http://localhost:8000/ to the Valid Post Logout Redirect URIs.
Under the django-app client, go to the Roles tab and create a new role named librarian.
Create a user in Keycloak and assign them the librarian role from the django-app client.
API Endpoints
The following API endpoints are available:

Endpoint	Method	Description	Permissions Required
/api/books/	GET	List all books.	Authenticated, librarian
/api/books/	POST	Create a new book.	Authenticated, librarian
/api/books/<id>/	GET	Retrieve a specific book.	Authenticated, librarian
/api/books/<id>/	PUT	Update a specific book.	Authenticated, librarian
/api/books/<id>/	DELETE	Delete a specific book.	Authenticated, librarian
/api/profile/	GET	Retrieve the current user's profile.	Authenticated
/api/profile/	PUT	Update the current user's profile.	Authenticated
/api/token/	POST	Obtain JWT access and refresh tokens.	Public
/api/token/refresh/	POST	Refresh an access token.	Public
/api/logout/	POST	Blacklist a refresh token to log out.	Authenticated

