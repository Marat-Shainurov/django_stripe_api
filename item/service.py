import stripe
from stripe.error import StripeError

from config import settings


class ProjectStripeError(Exception):
    pass


class ProjectStripeSession:
    """
    A class isolating the Stripe session creation process.
    Has all the methods needed to create a Stripe session object.
    The _create_stripe_product, _create_stripe_price, _create_stripe_session methods are used within the class.
    The make_session() method can be used externally.
    """

    def __init__(self, obj_name: str, obj_price: float):
        self.API_KEY = settings.STRIPE_API_KEY
        self.obj_name = obj_name
        self.obj_price = int(obj_price)
        stripe.api_key = settings.STRIPE_API_KEY

    def __create_stripe_product(self) -> dict:
        """Creates a new stripe product object"""
        try:
            stripe_product = stripe.Product.create(name=self.obj_name)
            return stripe_product
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe product: {str(e)}')

    def __create_stripe_price(self) -> dict:
        """Creates a new strip price object"""
        stripe_product = self.__create_stripe_product()
        try:
            stripe_price = stripe.Price.create(
                unit_amount=self.obj_price,
                currency="usd",
                product=f"{stripe_product['id']}",
            )
            return stripe_price
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe price: {str(e)}')

    def __create_stripe_session(self) -> dict:
        """Creates a new stripe session."""
        stripe_price = self.__create_stripe_price()
        try:
            stripe_session = stripe.checkout.Session.create(
                success_url="https://example.com/success",
                line_items=[
                    {
                        "price": f"{stripe_price['id']}",
                        "quantity": 1,
                    },
                ],
                mode="payment",
            )
            return stripe_session
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe session: {str(e)}')

    def make_session(self):
        """Creates and returns a new stripe session."""
        return self.__create_stripe_session()
