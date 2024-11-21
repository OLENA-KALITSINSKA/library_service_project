# Library Management System

This is a web-based library management system designed to streamline the management of books, borrowings, users, and payments. The system helps library administrators track book inventory, manage user borrowings, and handle payments efficiently. The goal of this system is to replace the outdated manual tracking system and optimize library operations.

## Features

- **Manage Books Inventory**: Add, update, and delete books. View the list of available books.
- **Book Borrowing Management**: Allow users to borrow books and track due dates.
- **Manage Customers**: Register users, authenticate with JWT, and manage user profiles.
- **Notifications**: Notifications for new borrowings through Telegram.
- **API Endpoints**: A well-defined REST API for managing books, users and borrowings.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Obtain a token by posting login credentials to:

- **get token**: http://127.0.0.1:8000/api/user/token/
- **refresh token**: http://127.0.0.1:8000/api/user/token/refresh/
- **create user**: http://127.0.0.1:8000/api/user/

Include the token in the `Authorization` header for subsequent requests using the `Bearer` scheme. For example:

`Authorization: Bearer <your_token>`

#### **Book**
- Title: `str`
- Author: `str`
- Cover: Enum (`HARD | SOFT`)
- Inventory: `positive int`
- Daily fee: `decimal` (in USD)

#### **User (Customer)**
- Email: `str`
- First Name: `str`
- Last Name: `str`
- Password: `str`
- Is Staff: `bool`

#### **Borrowing**
- Borrow Date: `date`
- Expected Return Date: `date`
- Actual Return Date: `date`
- Book ID: `int`
- User ID: `int`


## Services

- **Books Service**: CRUD operations for managing books.
- **Users Service**: Manage authentication, user registration, and profiles.
- **Borrowings Service**: Manage book borrowings and returns.
- **Notifications Service**: Send notifications for borrowing actions using Telegram.

## API Endpoints

### **Books Service**
- `POST /books/`: Add a new book.
- `GET /books/`: List all books.
- `GET /books/<id>/`: Get detailed information about a specific book.
- `PUT/PATCH /books/<id>/`: Update book details (inventory management).
- `DELETE /books/<id>/`: Delete a book.

### **Users Service**
- `POST /users/`: Register a new user.
- `POST /users/token/`: Get JWT tokens for authentication.
- `POST /users/token/refresh/`: Refresh JWT token.
- `GET /users/me/`: Get user profile information.
- `PUT/PATCH /users/me/`: Update user profile.

### **Borrowings Service**
- `POST /borrowings/`: Borrow a book.
- `GET /borrowings/?user_id=...&is_active=...`: List borrowings for a specific user.
- `GET /borrowings/<id>/`: Get detailed information about a borrowing.
- `POST /borrowings/<id>/return/`: Return a borrowed book.


### **Notifications Service**
- Send notifications to Telegram on borrowing creation.

## Requirements

- Python 3.x
- Django 4.x
- Python-dotenv for environment variable management
- Telegram API for notifications
- JWT authentication

## API Documentation
- **Swagger**: [http://127.0.0.1:8000/api/doc/swagger/](http://127.0.0.1:8000/api/doc/swagger/)
- **ReDoc**: [http://127.0.0.1:8000/api/doc/redoc/](http://127.0.0.1:8000/api/doc/redoc/)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/OLENA-KALITSINSKA/library_service_project.git
cd library-management-system
```
#### Building and Running the Docker Container

1. **Build the Docker Images**:
    ```bash
    docker-compose build
    ```

2. **Start the Containers**:
    ```bash
    docker-compose up
    ```

   This command will start both the Django application and the PostgreSQL database.

3. **Create a Superuser** (if needed):
   Open a new terminal window and run:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

4. **Access the Application**:
   Open your browser and go to `http://127.0.0.1:8000` to see the application running.

#### Stopping the Containers

To stop the containers, run:
```bash
docker-compose down
```

### Additional Information

- **Testing**: To run tests, use `python manage.py test`.
