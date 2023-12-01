import stripe
from stripe import TaxRate
from stripe.api_resources.checkout import Session
from stripe.error import StripeError

from config import settings
from config.settings import SMALLEST_CURRENCY_UNIT_RATIO
from item.models import Item


class ProjectStripeError(Exception):
    pass


class ProjectStripeSession:
    """
    A class isolating the Stripe session creation process.
    Is suitable both for a single item purchase and a multi-items order.
    Has all the methods needed to create a Stripe session object.
    The make_session() method can be used externally. All the other methods are used within the class.
    """

    def __init__(self, items: list[Item], tax=None, discount=None):
        """
        Initializes a ProjectStripeSession instance.
        Used for creating a stripe.checkout.Session.create session.

        :param items: a list of item.Item instances.
        :param tax: a pricing.Tax model instance.
        :param discount: a pricing.Discount model instance.
        """
        self.API_KEY = settings.STRIPE_API_KEY
        self.items = items
        if tax is not None:
            self.tax_behavior = 'exclusive'
        else:
            self.tax_behavior = 'inclusive'
        self.tax = tax
        self.discount = discount
        # Currency's smallest unit ratio. Set at the level of 100 as the default value.
        # For example, there are 100 pennies to one usd dollar. Same works for one rub.
        self.smallest_cur_unit_ratio = SMALLEST_CURRENCY_UNIT_RATIO
        self.conversion_rate = 0.011

        stripe.api_key = settings.STRIPE_API_KEY

    def __convert_to_common_currency(self, item: Item) -> tuple:
        """
        Auxiliary method to convert an item's currency the common value ('usd').
        Used in self.__create_stripe_product_list when the self.items list of Item instances contain items
        with different currencies.

        :param item: an item.Item instance.
        """
        if item.currency == 'usd':
            return int(item.price) * self.smallest_cur_unit_ratio, 'usd'
        else:
            converted_price = int(item.price) * self.smallest_cur_unit_ratio * self.conversion_rate
            return converted_price, 'usd'

    def __create_stripe_tax(self) -> TaxRate:
        """
        Creates a Stripe TaxRate instance, based on the self.tax instance fields' values.
        If self.tax passed the method is used in self.__create_stripe_session.

        :return: a TaxRate instance
        """
        stripe_tax = stripe.TaxRate.create(
            percentage=self.tax.rate,
            description=f'Tax {self.tax.id}',
            display_name=f'Tax {self.tax.id}',
            inclusive=False,
        )
        return stripe_tax

    def __create_stripe_product(self) -> dict:
        """
        Creates a new Stripe Product object.
        The method is used when only one Item object is passed.

        :return: a dict (stripe_product response with extra 'item_price' and 'item_currency' key-val pairs).
        """
        try:
            stripe_product = stripe.Product.create(name=self.items[0].name)
            stripe_product['item_price'] = int(self.items[0].price) * self.smallest_cur_unit_ratio
            stripe_product['item_currency'] = self.items[0].currency
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe product: {str(e)}')

        return stripe_product

    def __create_stripe_product_list(self) -> list[dict]:
        """
        Creates a list of Stripe Product object.
        The method is used when several Item object are passed as an order.
        If all the items have the same currency - their set currency is used (usd or rub).
        If all the items have different currencies - usd currency is used as the common currency via the
        self.__convert_to_common_currency method, in order to avert issues during the Checkout Session creation.

        :return: a list of dicts (stripe_product responses with extra 'item_price' and 'item_currency' key-val pairs)
        """
        stripe_products_list = []
        items_have_same_currency = len({item.currency for item in self.items}) == 1

        for item in self.items:
            try:
                stripe_product = stripe.Product.create(name=item.name)
                if not items_have_same_currency:
                    converted_price = self.__convert_to_common_currency(item)
                    stripe_product['item_price'] = int(converted_price[0])
                    stripe_product['item_currency'] = converted_price[1]
                else:
                    stripe_product['item_price'] = int(item.price) * self.smallest_cur_unit_ratio
                    stripe_product['item_currency'] = item.currency
                stripe_products_list.append(stripe_product)
            except StripeError as e:
                raise ProjectStripeError(f'Error during creating Stripe product: {str(e)}')

        return stripe_products_list

    def __create_stripe_price_list(self) -> list[dict]:
        """
        Creates a list of Strip Price objects.

        :return: a list of Stripe Price objects.
        """
        stripe_prices_list = []
        if len(self.items) == 1:
            stripe_products = [self.__create_stripe_product()]
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

    def __create_stripe_discount(self):
        """
        Creates a Stripe Coupon object, based on the self.discount (pricing.Discount) instance fields' values.
        If the self.discount.amount_off is set the discount's currency is also configured:
        - If a single item is being purchased the self.item.currency is used as the amount_off currency.
        - If all the items have the same currency - their set currency is used (usd or rub).
        - If all the items have different currencies - usd currency is set as the common currency for the discount.

        :return: a Stripe Coupon object.
        """
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

    def __create_stripe_session(self) -> Session:
        """
        Creates a new Stripe Checkout Session, based on all the passed arguments.
        Calls self.__create_stripe_price_list() method to create stripe Product and Price instances.
        Calls self.__create_stripe_discount() and self.__create_stripe_tax() if self.discount and self.tax are provided.

        :return: a Stripe Checkout Session instance.
        """
        stripe_prices = self.__create_stripe_price_list()
        stripe_discounts = self.__create_stripe_discount() if self.discount else None
        stripe_tax = self.__create_stripe_tax() if self.tax else None
        try:
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                success_url="https://example.com/success",
                line_items=[
                    {
                        "price": f"{price['id']}",
                        "quantity": 1,
                        'tax_rates': [stripe_tax['id']] if self.tax else None
                    } for price in stripe_prices],
                mode="payment",
                discounts=[{'coupon': stripe_discounts['id']}] if self.discount else None)
            return stripe_session
        except StripeError as e:
            raise ProjectStripeError(f'Error during creating Stripe session: {str(e)}')

    @staticmethod
    def get_payment_status(session_id: str) -> bool:
        """
        Checks whether a payment has been made or not.
        Retrieves the Stripe Checkout Session by its id.

        :param session_id: a Stripe Checkout Session id.
        :return: True is session['payment_status'] == 'paid', otherwise returns False
        """
        stripe.api_key = settings.STRIPE_API_KEY
        payment_info = stripe.checkout.Session.retrieve(session_id)
        return payment_info['payment_status'] == 'paid'

    def make_session(self):
        """
        Creates and returns a new Stripe Checkout Session,
        with all the provided arguments during the class instance initialization.
        The method us used externally in the project's views.
        """
        return self.__create_stripe_session()
