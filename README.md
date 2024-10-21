# Running

Ensure Python and pip are installed

Install Django with `pip install django djangorestframwork` in an admin-level console

Navigate to the `backend` file inside a console

If running for the first time or changes have been made, run `py manage.py makemigrations` and `py manage.py migrate`

Run `py manage.py runserver`

Navigate to the development server at localhost:8000/api/

# Developing

Inside `api/models.py` define the models for the SQL database, and make their serializers in `api/serializer.py`

Inside `api/urls.py` define the endpoints for the API

Inside `api/views.py` write the logic behind the endpoints
