# General description

django_stripe_api is a service for buying single items or multi-item orders. \
Main stack: Django, Postgres, Celery, Celery-Beat, Redis, Docker.
Integrated APIs: Stripe API (for handling checkouts), fixer.io API (for getting latest currency rates).

# Install and usage

1. **Clone** the project from https://github.com/Marat-Shainurov/drf_library to your local machine.

2. Create **.env** file in the root directory (next to the docker-compose file) with the variables from .env_sample.
    - You have to add your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. EMAIL_HOST configured in the project - '
      smtp.yandex.ru'.
    - You have to add MYSQL_DATABASE and MYSQL_ROOT_PASSWORD variables for the database setup.

3. Build and run a new **docker** image from the project's root directory:
    - docker-compose up --build

    3307 port is used for the database outside the docker container, in case the standard 3306 port is already in use.

4. After successful startup check out the project's endpoints (swagger or redoc **documentation** formats are
   available):
    - [Swagger Documentation] http://127.0.0.1:8000/docs/
    - [ReDoc Documentation] http://127.0.0.1:8000/redoc/

5. Start working with the app's endpoints:

      **users (authorization is not required)** 
    - [Register User] http://127.0.0.1:8000/users/register
    - [Get Token] http://127.0.0.1:8000/users/token 

      **library (authorization is required, can be tested via Postman, with Bearer token provided from users/token)**
    - [Books List] http://127.0.0.1:8000/library/books
    - [Create Book] http://127.0.0.1:8000/library/books/create
    - [Get Book by ID] http://127.0.0.1:8000/library/books/get/{id}
    - [Update Book by ID (both PATCH and PUT methods)] http://127.0.0.1:8000/library/books/update/{id}
    - [Delete Book by ID] http://127.0.0.1:8000/library/books/delete/{id} 

      **admin site** is also configured 
    - [Admin interface] http://127.0.0.1:8000/admin

# Fixture

1. If necessary the testing fixture may be loaded (with 2 CustomUser and 2 Book testing instances):
    - docker-compose exec app python manage.py loaddata test_fixture.json
2. Testing users and credentials:
    - {"username": "test_superuser", "password": "123"}
    - {"username": "test_user", "password": "QWE123qwe123!"}

# Testing

1. All the endpoints are covered with unittests in users/tests.py and library/tests.py
2. Run tests from the running docker container:
    - docker-compose exec app python manage.py test

