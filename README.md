# FastAPI To-Do Application with Automated Deployment

A simple To-Do list application built with FastAPI, allowing users to create, read, update, and delete tasks.
Running on docker containers. Deployment is automated via Github Actions.

## Requirements

* Docker
* Docker-compose
* Python 3.11
* Poetry (python-poetry)

## Features

- User authentication (login and registration)
- Create, read, update, and delete tasks
- Assign tasks to users
- Set task completion status
- Role-based access control (admin and user roles)
- Daily reminders for incomplete tasks

## Setup

### Step 1: Configure ENV variables

Create a file ".env" (in the project's root directory, not inside "todo-list-app") with the following variables:

```bash
app_url=URL (Optional) # The app's domain, defaults to localhost

db_database=DATABASE
db_user=DB_USER
db_password=USER_PASSWORD

test_db_database=TEST_DATABASE
test_db_user=TEST_DB_USER
test_db_password=TEST_USER_PASSWORD

admin_username=ADMIN_USERNAME (Optional)
admin_email=ADMIN_USER_EMAIL (Optional)
admin_password=ADMIN_USER_PASSWORD (Optional)  
secret_key="random string" (Optional) 

mail_from_address=FROM_ADDRESS # Sender address from Mailtrap
mail_token=TOKEN # Mailtrap API Token 
```
A test database will be created as well. If admin username, email and password are not provided, default values will be used. The secret key can be generated by running: 
```bash
openssl rand -hex 32  
```
Otherwise, a random string will be generated.

### Step 2: Start the containers

Start the containers by running:

```bash
docker-compose up -d
```
After the databases are up, the app will be started. The app is accessible on port 8000.


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

We use `pytest` for running tests. To run the tests, follow these steps (inside the todo-list-app directory):

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

To run linter checks, follow these steps (inside the todo-list-app directory)::

1.  **Install dependencies**:

If not done in the previous step, install the dependencies:
```bash
poetry install --with dev
```

2.  **Run `pylint`**:

```bash
poetry run pylint *.py **/*.py
```

## Automation with GitHub Actions

This project leverages GitHub Actions to automate the deployment process of the application. Below is a step-by-step overview of the workflow:
1. **Setup Testing Database:** A PostgreSQL service is initialized for running tests.
2. **Code Quality and Testing:** Linter checks and pytest are executed to ensure code quality and functionality.
3. **VPN Connection (Optional):** The runner connects to a VPN if required for accessing the infrastructure.
4. **Access Remote Infrastructure:** The deployment targets an OpenNebula environment.
5. **Instance Deployment:** Terraform provisions a new virtual machine (VM) instance.
6. **Application Deployment:** Ansible configures the VM and deploys the application.

## Requirements

To use this workflow, ensure the following prerequisites are met:

- **OpenNebula Access:** A configured OpenNebula instance to provision VMs.
- **VPN Access (Optional):** If VPN is required, OpenConnect must be used to generate a session cookie.
- **VM Template:** A Debian 12-based VM template in OpenNebula, including an additional unformatted drive mounted as /dev/sdb (optional for disk preparation).
- **Secrets and Variables Configuration:** Required secrets and variables should be configured in GitHub Actions.

### Secrets and Variables

#### Secrets
The following secrets must be set in your GitHub repository:

- `ENV_FILE`: The contents of the .env file as outlined in the project setup.
- `POSTGRES_DB`: Database name for testing.
- `POSTGRES_PASSWORD`: Password for the testing database user.
- `POSTGRES_USER`: User for the testing database.
- `SSH_PRIVATE_KEY`: Private SSH key for connecting to deployed servers (matches the public key in the VM template context).
- `TERRAFORM_VARIABLES`: The full contents of the terraform.tfvars file for Terraform configuration.
- `VPN_SERVER`: Hostname of the VPN server.

Sample terraform.tfvars file:
```bash
endpoint      = "http://example.com:2633/RPC2"
flow_endpoint = "http://example.com"
username      = "user"
password      = "password"
template_id   = 1234
op_group      = "group-1"
```

#### Variables

The following variables control optional steps in the workflow:

- `VPN_REQUIRED`: Set to true or false to enable or skip VPN connection steps.
- `FORMAT_AND_MOUNT_DISKS`: Set to true or false to enable or skip disk preparation on the deployed VM.
