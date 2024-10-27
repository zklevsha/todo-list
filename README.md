# FastAPI To-Do Application

A simple To-Do list application built with FastAPI, allowing users to create, read, update, and delete tasks.

## Requirements

* Python 3.11
* Python 3.11 devel package (python3.11-devel for Fedora-based distros, python3.11-dev Debian-based)
* Poetry (python-poetry) for managing dependencies
* Docker-compose

## Features

- User authentication (login and registration)
- Create, read, update, and delete tasks
- Assign tasks to users
- Set task completion status
- Role-based access control (admin and user roles)
- Daily reminders for incomplete tasks

## Setup

### Step 1: Create and activate the Virtual Environment

To create and enter the virtual environment, run:
```bash
poetry shell
```

### Step 2: Install the dependencies
Install the dependencies:

```bash
poetry install
```
If you don't want to install the "dev" dependencies, run:
```bash
poetry install --only main
```

### Step 3: Configure ENV variables

Create a file ".env" with the following variables:

```bash
app_url=URL (Optional) # The app domain, defaults to localhost

db_host=HOST
db_database=DATABASE
db_user=DB_USER
db_password=USER_PASSWORD

test_db_database=TEST_DATABASE
test_db_user=TEST_DB_USER
test_db_password=TEST_USER_PASSWORD

admin_username=ADMIN_USERNAME (Optional)
admin_email=ADMIN_USER_EMAIL (Optional)
admin_password=ADMIN_USER_PASSWORD (Optional)  
secret_key = "random string"

mail_from_address=FROM_ADDRESS # Sender address from Mailtrap
mail_token=TOKEN # Mailtrap API Token
```
A test database will be created as well. If admin username, email and password are not provided, default values will be used. The secret key can be generated by running: 
```bash
openssl rand -hex 32  
```

### Step 4: Start the PostgreSQL container

Start the docker container and wait for the migration to conclude:

```bash
docker-compose up -d
```

### Step 5: Apply Database Migrations (Alembic)

Run the migration command:

```bash
alembic upgrade head
```

### Step 6: Run the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn app:app --reload
```


### Endpoints

#### Miscellaneous Routes

| Method | Endpoint              | Description           | Authentication Required |
|--------|-----------------------|-----------------------|-------------------------|
| `GET`  | `/api/v1/`            | Root Test             | No                      |
| `GET`  | `/api/v1/schema`      | Get Schema Version    | No                      |

#### Tasks

| Method  | Endpoint                   | Description        | Authentication Required |
|---------|----------------------------|--------------------|-------------------------|
| `GET`   | `/api/v1/tasks/`           | Get All Todos      | Yes                     |
| `POST`  | `/api/v1/tasks/`           | Add Todo           | Yes                     |
| `GET`   | `/api/v1/tasks/{task_id}`  | Get Task by Id     | Yes                     |
| `PUT`   | `/api/v1/tasks/{task_id}`  | Update Todo        | Yes                     |
| `DELETE`| `/api/v1/tasks/{task_id}`  | Delete Todo        | Yes    |
| `PUT`   | `/api/v1/tasks/{task_id}/finish` | Mark Completed | Yes                   |

#### Users

| Method   | Endpoint                       | Description               | Authentication Required |
|----------|--------------------------------|---------------------------|-------------------------|
| `POST`   | `/api/v1/users/register`       | Create User               | No                      |
| `GET`    | `/api/v1/users/{id_}`          | Get User                  | No                      |
| `PUT`    | `/api/v1/users/{id_}`          | Update User               | Yes     |
| `DELETE` | `/api/v1/users/{id_}`          | Delete User               | Yes    |
| `POST`   | `/api/v1/users/reminders`  | Configure daily reminders | Yes     |
| `PATCH`  | `/api/v1/users/{id_}`          | Set Role                  | Yes (Admin only)        |
| `GET`    | `/api/v1/users/`               | Get All Users             | Yes (Admin only)        |
| `POST`   | `/api/v1/users/send_reminders` | Send daily reminders      | Yes (Admin only)        |

#### Authentication

| Method  | Endpoint                   | Description        | Authentication Required |
|---------|----------------------------|--------------------|-------------------------|
| `POST`  | `/api/v1/login`            | Login              | No                      |

## Authentication

To access endpoints that require authentication, you need to include a valid JWT token in the `Authorization` header as a Bearer token. The "login" endpoint generates a new token with a default expiration of 7 days. 

Example of a user login request using curl:
```bash
curl -i localhost:8000/api/v1/login -XPOST -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=USERNAME&password=PASSWORD' -w '\n'
```
The above will generate a new token. 

## Daily Reminders

The daily reminder feature sends an automated email to users who have the `daily_reminder` option enabled. It aggregates all incomplete tasks for each user and sends a summary in the email body. The reminders are triggered via a background scheduler that runs at a configured interval. The scheduler calls the `/send_reminders` API, which queries the database for users with pending tasks and sends the appropriate emails.
The emails are sent using the Mailtrap service. The sender's email and API token can be configured/obtained here: https://mailtrap.io/sending/domains

## Sample Requests (Curl)

Register a new user:
```bash
curl -i localhost:8000/api/v1/users/register -XPOST -H 'Content-Type: application/json' -d '{"username": "user", "email": "test@test.com", "password": "password"}' -w '\n'
```

Update user - in this case, the email of user with ID 2:
```bash
curl -i localhost:8000/api/v1/users/2 -XPUT -H 'Content-Type: application/json' -d '{"email":"test2@test.com"}' -H "Authorization: Bearer $token" -w '\n'
```

Delete user with ID 2:
```bash
curl -i localhost:8000/api/v1/users/2 -XDELETE -H 'Content-Type: application/json' -H "Authorization: Bearer $token" -w '\n'
```

Enable the daily reminders:
```bash
curl -i localhost:8000/api/v1/users/reminders -XPOST -H 'Content-Type: application/json' -H "Authorization: Bearer $token" -d '{"reminder":"yes"}' -w '\n'
```

Get all tasks:
```bash
curl -i localhost:8000/api/v1/tasks/ -XGET -H 'Content-Type: application/json' -H "Authorization: Bearer $token" -w '\n'
```

Add a new task:
```bash
curl -i localhost:8000/api/v1/tasks/ -XPOST  -H 'Content-Type: application/json' -H "Authorization: Bearer $token" -d '{"title":"Title", "description":"Description", "is_finished": "False"}' -w '\n'
```

Mark task as completed:
```bash
curl -i localhost:8000/api/v1/tasks/1/finish -XPUT -H 'Content-Type: application/json' -H "Authorization: Bearer $token" -d '{"is_finished": "True"}' -w '\n'
```


## Contributions

Unit tests were added to the project. Also, linter checks might be performed by following the instructions provided below.

### Running Tests

We use `pytest` for running tests. To run the tests, follow these steps:

1.  **Install dependencies**:

Make sure you have all the necessary dependencies installed.
```bash
poetry install --with dev
```

2.  **Run the tests**:
To run all the tests, run:
```bash
poetry run pytest -v
```

### Running Linter Checks

To run linter checks, follow these steps:

1.  **Install dependencies**:

If not done in the previous step, install the dependencies:
```bash
poetry install --with dev
```

2.  **Run `pylint`**:

```bash
poetry run pylint *.py **/*.py
```
