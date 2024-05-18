
# FastAPI Application

A basic FastAPI application set up with test endpoints.

## Setup

### Step 1: Create and activate the Virtual Environment

First, create a virtual environment:

```bash
python3 -m venv todo_list
source todo_list/bin/activate 
```
### Step 2: Install the dependencies

Install the dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt 
```
### Step 3: Run the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn fast_api_test:app --reload
```
## Endpoints

The application can be tested using `curl`:

### Root Endpoint

To test the root endpoint:

```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/ 
```
Expected response:

```json
`{"message":"This is the root endpoint."}` 
```
### Test Route

To test the `/test` route:

```bash
curl -XGET -H 'Content-Type: application/json' -w '\n' localhost:8000/test 
```

Expected response:

```json
`{"message":"This is another test route."}` 
```