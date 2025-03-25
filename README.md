# Django Spam & Contact Search API

## Description
This project is a Django REST API for a mobile application that allows users to check phone numbers for spam, search for contacts by name or phone number, and mark numbers as spam. It features user registration, token-based authentication, and a global database combining all registered users and their contacts. A management command is also provided to populate the database with sample data for testing.

## Features
- **User Registration & Profile:**  
  - Register with name, unique phone number, optional email, and password.
  - Custom user model with token-based authentication.
  
- **Contacts & Global Database:**  
  - Each registered user can have multiple personal contacts.
  - Global search across registered users and contacts.
  
- **Spam Reporting:**  
  - Users can mark any phone number as spam.
  - Aggregated spam count per phone number.
  
- **Search Functionality:**  
  - **By Name:** Returns results ordered with names starting with the query first, then those containing the query.
  - **By Phone Number:** If the phone number is registered, returns that user; otherwise, returns matching contacts.
  - **Detailed Person View:** Shows full details, with email only displayed for registered users if the requester is in that user's contact list.
  
- **Data Population:**  
  - A management command to generate random sample data (users, contacts, and spam reports) for testing.

## Requirements
- Python 3.8+
- Django (3.x or 4.x)
- Django REST Framework
- SQLite (default) or any other relational database supported by Django

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://your.repo.url.git
   cd django-spam-contact-api
   ```
2. **Create and Activate a Virtual Environment:**  
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```
3. **Install Dependencies:**
    Create a `requirements.txt` with the following (or similar) packages:
    ```nginx
    Django
    djangorestframework
    djangorestframework-authtoken
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```
4. **Apply Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5. **Create a Superuser (Optional):**
    ```bash
    python manage.py createsuperuser
    ```
6. **Populate Sample Data (Optional):**
    ```bash
    python manage.py populate_data
    ```
7. **Running the Server:**
    Start the development server with:
    ```bash
    python manage.py runserver
    ```

## API Endpoints
- **User Registration**  
  - Endpoint: `POST /api/register/`
  - Payload Example:
    ```json
    {
     "name": "Alice Example",
     "phone_number": "1234567890",
     "email": "alice@example.com",
     "password": "yourpassword"
    }
    ```
    - Response: JSON containing user details (ID, name, phone number, email).

- **User Login**
    - Endpoint: `POST /api/login/`
    - Payload Example:
        ```json
        {
         "phone_number": "1234567890",
         "password": "yourpassword"
        }
        ```
        - Response: JSON with an authentication token.

- **Search by Name**
    - Endpoint: `GET /api/search/name/?q=Alice`
    - Headers: `Authorization: Token
        your_token_here`
    - Response: An array of matching registered users and contacts.

- **Search by Phone Number**
    - Endpoint: `GET /api/search/phone/?q=1234567890`
    - Headers: `Authorization: Token
        your_token_here`
    - Response: Details of the registered user (if exists) or matching contacts.

- **Detailed Person View**
    - Endpoint: `GET /api/person/<id>/`
    - Headers: `Authorization: Token
        your_token_here`
    - Response: Full details for the person. For a registered user, the email is shown only if the requester is in that user's contact list.

- **Spam Reporting**
    - Endpoint: `POST /api/spam/`
    - Headers: `Authorization: Token
        your_token_here`
    - Payload Example:
        ```json
        {
         "phone_number": "0987654321"
        }
        ```
        - Response: Confirmation message that the number has been marked as spam.

## Testing the API
Use `curl`, Postman, or the Django REST Framework's browsable API.

Ensure you include the token in the `Authorization` header for all endpoints (except registration and login).

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is open-source and available under the [MIT License](LICENSE).