
# FastAPI Application

A basic FastAPI application set up with test endpoints interacting with a PostgreSQL database running on a docker container. 
## Requirements

* Python 3.11
* Python 3.11 devel package (python3.11-devel for Fedora-based distros, python3.11-dev Debian-based)
* Docker-compose
* Curl

## Setup

### Step 1: Create and activate the Virtual Environment

To create and enter the virtual environment, run:

```bash
python3 -m venv .venv
source .venv/bin/activate 
```
### Step 2: Install the dependencies

Install the dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt 
```
### Step 3: Configure ENV variables

Create a file ".env" with the following variables (a test database will be created as well):

```bash
db_host=HOST  
db_database=DATABASE  
db_user=DB_USER  
db_password=USER_PASSWORD  

test_db_database=TEST_DATABASE
test_db_user=TEST_DB_USER
test_db_password=TEST_USER_PASSWORD
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

## Endpoints

The application can be tested using `curl`:

### Root Endpoint

```bash
curl -i localhost:8000/api/v1/ -XGET -H 'Content-Type: application/json' -w '\n' 
```
Expected response:

```json
`{"message":"This is the root endpoint."}` 
```
### Test Route


```bash
curl -i localhost:8000/api/v1/test -XGET -H 'Content-Type: application/json' -w '\n'  
```

Expected response:

```json
`{"message":"This is another test route."}` 
```
### Test connection to the PostgreSQL server


```bash
curl -i localhost:8000/api/v1/db-connection -XGET -H 'Content-Type: application/json' -w '\n' 
```

Expected response:

```json
`{"status":"success","message":"Successfully connected to the server."}` 
```
### Get current DB schema version
This endpoint returns the current DB schema version (integer) for the database specified in the ".env" file querying the "alembic_version" table.

```bash
curl -i localhost:8000/api/v1/schema -XGET -H 'Content-Type: application/json' -w '\n' 
```

Expected response:

```json
"4e0841682211"
```

## CRUD Operations

CRUD operations can be performed with the following endpoints:

### Get all existing tasks
```bash
curl -i localhost:8000/api/v1/tasks -XGET  -H 'Content-Type: application/json' -w '\n'
```
The endpoint will provide a list with all the entries. 

### Create a new task
```bash
curl -i localhost:8000/api/v1/tasks -XPOST -H 'Content-Type: application/json' -d '{"title":"Title", "description":"Description", "creation_date":"2024-07-21T00:00:00", "is_finished": "False"}' -w '\n'
```
Only the title and description are mandatory. 

### Search for tasks by ID
```bash
curl -i localhost:8000/api/v1/tasks/1 -XGET  -H 'Content-Type: application/json' -w '\n'
```
Similar to the previous endpoint, but will return a specific entry based on its ID (if it exists). 

### Update an existing task
```bash
curl -i localhost:8000/api/v1/tasks/1 -XPUT -H 'Content-Type: application/json' -d '{"title":"Title", "description":"Description", "creation_date":"2024-07-21T00:00:00", "is_finished": "false"}' -w '\n'
```
A "PUT" request is required in this case. Once again, title and description are needed. 

### Set tasks as completed/pending
```bash
curl -i localhost:8000/api/v1/tasks/1/finish -XPUT -H 'Content-Type: application/json' -d '{"is_finished": "true"}' -w '\n'
```
This endpoint will mark a task as finished if it's not, and viceversa.  

### Delete tasks by ID
```bash
curl -i localhost:8000/api/v1/tasks/1 -XDELETE -H 'Content-Type: application/json' -w '\n'
```
This endpoint will delete a specific task, based on its ID (if it exists). 


## Contribution
Unit tests were added to the project. Also, linter checks might be performed by following the instructions provided below. 

### Running Tests

We use `pytest` for running tests. To run the tests, follow these steps:

1. **Install dependencies**:
    Make sure you have all the necessary dependencies installed.
    ```bash
    pip install -r requirements-dev.txt
    ```

2. **Run the tests**:
    To run all the tests, run:
    ```bash
    pytest -v
    ```

### Running Linter Checks

To run linter checks, follow these steps:

1. **Install dependencies**:
    If not done in the previous step, install the dependencies using the requirements-dev.txt file:
    ```bash
    pip install -r requirements-dev.txt
    ```

2. **Run `pylint`**:
    ```bash
    pylint *.py
    ```