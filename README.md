# General description

django_stripe_api is a service for buying single items or multi-item orders. \
Main stack: Django, Postgres, Celery, Celery-Beat, Redis, Docker.
Integrated APIs: Stripe API (for handling checkouts), fixer.io API (for getting latest currency rates).

# Install and usage

1. **Clone** the project from https://github.com/Marat-Shainurov/django_stripe_api to your local machine.

2. Create **.env** file in the root directory (next to the docker-compose file) with the variables from .env_sample. \
   **For convenience of checking the work** I kept the used env variables and their values in env_sample.

3. Build and startup a new **docker** container from the project's root directory:
    - docker-compose up --build

4. Start working with the app's endpoints:

    - **[Item Detail]** http://127.0.0.1:8000/item/{item_id} \
      You can get details about an Item and buy it.
      Test mode credit card number: 4242 4242 4242 4242; exp. date and cvv code - any data.
    - **[Buy Item]** http://127.0.0.1:8000/buy/{item_id} \
      Returns an object, type of: {'stripe_session_id': stripe_session['id'], 'checkout_url': stripe_session['url']}
    - **[Create Order]** http://127.0.0.1:8000/order/create \
      You can create and buy orders on this page. \
      Test mode credit card number: 4242 4242 4242 4242; exp. date, cvv code, client's info - any data. \
      Each created order is being checked for the payment status by periodic celery task every 2 minutes. \
      When the corresponding checkout session payment's status is changed from 'unpaid' to 'paid' 
      (i.e. the checkout session is paid by customer) the order instance's 'payment_status' field is set to the 'paid' status. \
      The expiration period is set to 30 minutes both for the Stripe Checkout Session and the payment status check periodic task. 
    - **[Admin interface]** http://127.0.0.1:8000/admin

# Fixture

1. The fixture loading is already included to the docker startup process (python manage.py loaddata > test_fixture.json).
    - 4 testing Item instances are created, 3 Discount items, 3 Tax instances. 
    - Use them or create new instances from the admin interface.
    - Orders must be created only from the order/create endpoint.
2. Testing superuser credentials:
    - {"username": "test_superuser", "password": 123}. Use these credentials for the admin site.

# Deployment

1. The project is also deployed on the virtual machine (158.160.15.108):
   - **[Item Detail]** http://158.160.15.108/item/{item_id}
   - **[Buy Item]** http://158.160.15.108/buy/{item_id}
   - **[Create Order]** http://158.160.15.108/order/create
   - **[Admin interface]** http://158.160.15.108/admin