- Created the backend and frontend folders

- In Backend

1. Created venv named .venv
2. pip install fastapi uvicorn "sqlalchemy>=2" pydantic "python-multipart" 
3. Fastapi backend app MVC files are created
4. Database will be loaded from the CRUD App script, and the load_data.py script is also kept here for reference. If required the Data CSV files can be loaded.

Following activities are done on the thozhilmate_js folder

Command to run the backend:

python -m uvicorn app.main:app --reload --app-dir fastapi_backend --port 8000

The fastapi places the db unders thozhilmate_js folder. This folder will be the 
root folder, as it can access both fastapi_backend and react_frontend

Command to load the data into Database:

To populate the database tables for testing we will use load_data.py script. This is 
also in the root folder

Testing the Database after loading Data:

crud_app_05.py is used for testing whether all the data has successfully loaded into
the database

Setting up the Frontend:

Get Nodejs installed:

https://nodejs.org/en/download

Setup the framework:

npm create vite@latest . -- --template react-ts