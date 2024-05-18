
# FastAPI Application

A basic FastAPI application set up with test endpoints interacting with a PostgreSQL database running on a docker container. 

## Setup

### Step 1: Create and activate the Virtual Environment

To create and enter the virtual environment, run:

```bash
python3 -m venv todo_list
source todo_list/bin/activate 
```
### Step 2: Install the dependencies

Install the dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt 
```
### Step 3: Configure ENV variables

Create a file ".env" with the following variables:

```bash
host=HOST  
database=DATABASE  
user=DB_USER  
password=USER_PASSWORD  
```

### Step 4: Start the PostgreSQL container

Start the docker container and wait for the migration to conclude:

```bash
docker-compose up -d
```
### Step 5: Run the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn fast_api_test:app --reload
```

## Endpoints

The application can be tested using `curl`:

### Root Endpoint

```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/ 
```
Expected response:

```json
`{"message":"This is the root endpoint."}` 
```
### Test Route


```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/test 
```

Expected response:

```json
`{"message":"This is another test route."}` 
```
### Test connection to the PostgreSQL server


```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/db_test_connection 
```

Expected response:

```json
`{"status":"success","message":"Successfully connected to the server."}` 
```
### Get current DB schema version
This endpoint returns the current DB schema version (integer) for the database specified in the ".env" file.

```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/db_schema_version 
```

Expected response:

```json
1
```