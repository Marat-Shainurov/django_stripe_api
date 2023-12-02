from django.core.exceptions import ValidationError
from django.views import generic

from config.settings import SMALLEST_CURRENCY_UNIT_RATIO
from order.service import ProjectStripeSession
from order.forms import OrderForm
from order.models import Order
from order.tasks import set_payment_status_check_schedule, set_disabler_schedule


class CreateOrderView(generic.CreateView):
    model = Order
    form_class = OrderForm
    extra_context = {'page_title': 'Create Order'}
    template_name = 'order/create_order.html'

    def get_success_url(self):
        """
        Sets the Stripe Checkout Session url as the successful url for the Order creating.
        The url is collected from the self.request.session object.
        """
        return self.request.session.get('checkout_url')

    def form_valid(self, form):
        """
        Checks whether the form is valid, assigns the 'total_price', 'currency' fields values to the Order instance,
        sets the schedule of the periodic task (set_payment_status_check_schedule) to monitor the payment_status of the
        Stripe Checkout Session, and the schedule of the one-off task (set_disabler_schedule) to disable the
        set_payment_status periodic task if the Order is paid of the payment expired (exp time - 30 minutes).
        """
        self.object = form.save()
        if form.is_valid():
            items = form.cleaned_data.get('items', [])
            discount = form.cleaned_data.get('discount', None)
            tax = form.cleaned_data.get('tax', None)

            if items:
                project_stripe_obj = ProjectStripeSession(
                    items=items,
                    discount=discount,
                    tax=tax)
                stripe_session = project_stripe_obj.make_session()
                self.object.total_price = stripe_session['amount_total'] / SMALLEST_CURRENCY_UNIT_RATIO
                self.object.currency = stripe_session['currency']
                self.object.save()

                self.request.session['checkout_url'] = stripe_session['url']

                set_payment_status_check_schedule.delay(order_id=self.object.pk, stripe_session_id=stripe_session['id'])
                set_disabler_schedule.delay(order_id=self.object.pk)

                return super().form_valid(form)
            else:
                ValidationError('Select items for your order')
