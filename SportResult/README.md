
# Sports Result Project

This project will retrieve the  match results 
from various sports leagues in the 2020-2021 season. 
It does this by retrieving the results from various APIS.

# Usage


Create and activate virtual environment outside the project folder

     virtualenv -p python3 env
     . ./env/bin/activate

Install Python dependencies

     pip install -r requirements.txt

Create SQLite database, run migrations

     cd myapp
    ./manage.py migrate

Run Django dev server

    ./manage.py runserver

To use the app navigate to the url http://127.0.0.1:8000/results/