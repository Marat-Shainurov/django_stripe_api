import stripe
from stripe.error import StripeError

from config import settings


class ProjectStripeError(Exception):
    pass


class ProjectStripeSession:
    """
    A class isolating the Stripe session creation process.
    Is suitable both for a single item purchase and a multi-items order.
    Has all the methods needed to create a Stripe session object.
    The make_session() method can be used externally. All the other methods are used within the class.
    """

    def __init__(self, items: list, tax=None, discount=None, smallest_cur_unit_ratio=100):
        self.API_KEY = settings.STRIPE_API_KEY
        self.items = items
        if tax is not None:
            self.tax_behavior = 'exclusive'
        else:
            self.tax_behavior = 'inclusive'
        self.tax = tax
        self.discount = discount
        self.smallest_cur_unit_ratio = smallest_cur_unit_ratio
        self.conversion_rate = 0.011

        stripe.api_key = settings.STRIPE_API_KEY

    def __convert_to_common_currency(self, item):
        if item.currency == 'usd':
            return int(item.price) * self.smallest_cur_unit_ratio, 'usd'
        else:
            converted_price = int(item.price) * self.smallest_cur_unit_ratio * self.conversion_rate
            return converted_price, 'usd'

    def __create_stripe_product(self) -> list[dict]:
        """Creates a new stripe product object"""
        stripe_products_list = []
        try:
            stripe_product = stripe.Product.create(name=self.items[0].name)
            stripe_product['item_price'] = int(self.items[0].price) * self.smallest_cur_unit_ratio
            stripe_product['item_currency'] = self.items[0].currency
            stripe_products_list.append(stripe_product)
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe product: {str(e)}')

        return stripe_products_list

    def __create_stripe_product_list(self) -> list[dict]:
        """Creates a new stripe product object"""
        stripe_products_list = []
        items_have_same_cur = len({item.currency for item in self.items}) == 1

        for item in self.items:
            try:
                stripe_product = stripe.Product.create(name=item.name)
                converted_price = self.__convert_to_common_currency(item) if not items_have_same_cur else (
                    item.price, item.currency)
                stripe_product['item_price'] = int(converted_price[0])
                stripe_product['item_currency'] = converted_price[1]
                stripe_products_list.append(stripe_product)
            except StripeError as e:
                raise ProjectStripeError(f'Error during creating Stripe product: {str(e)}')
        return stripe_products_list

    def __create_stripe_price_list(self) -> list[dict]:
        """Creates a new strip price object"""
        stripe_prices_list = []
        if len(self.items) == 1:
            stripe_products = self.__create_stripe_product()
        else:
            stripe_products = self.__create_stripe_product_list()

        for product in stripe_products:
            try:
                stripe_price = stripe.Price.create(
                    unit_amount=product['item_price'],
                    currency=product['item_currency'],
                    product=f"{product['id']}",
                    tax_behavior=self.tax_behavior
                )
                stripe_prices_list.append(stripe_price)
            except StripeError as e:
                raise ProjectStripeError(f'Error during creating Stripe price: {str(e)}')
        return stripe_prices_list

    def __create_stripe_tax(self):
        pass

    def __create_stripe_discount(self):
        items_have_same_cur = len({item.currency for item in self.items}) == 1
        if len(self.items) == 1:
            amount_off_currency = self.items[0].currency
        else:
            if items_have_same_cur:
                amount_off_currency = self.items[0].currency
            else:
                amount_off_currency = 'usd'

        stripe_discount = stripe.Coupon.create(
            duration='once',
            percent_off=self.discount.percent_off if self.discount.percent_off else None,
            amount_off=int(
                self.discount.amount_off) * self.smallest_cur_unit_ratio if self.discount.amount_off else None,
            currency=amount_off_currency
        )

        return stripe_discount

    def __create_stripe_session(self) -> dict:
        """Creates a new stripe session."""
        stripe_prices = self.__create_stripe_price_list()
        stripe_discounts = self.__create_stripe_discount() if self.discount else None
        try:
            stripe_session = stripe.checkout.Session.create(
                success_url="https://example.com/success",
                line_items=[{"price": f"{price['id']}", "quantity": 1} for price in stripe_prices],
                mode="payment",
                discounts=[{'coupon': stripe_discounts['id']}] if self.discount else None
            )
            return stripe_session
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe session: {str(e)}')

    def make_session(self):
        """Creates and returns a new stripe session with all the passed settings."""
        return self.__create_stripe_session()
