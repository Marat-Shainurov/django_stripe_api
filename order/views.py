from django.core.exceptions import ValidationError
from django.views import generic

from config.settings import SMALLEST_CURRENCY_UNIT_RATIO
from order.service import ProjectStripeSession
from order.forms import OrderForm
from order.models import Order
from order.tasks import set_payment_status_check_schedule


class CreateOrderView(generic.CreateView):
    model = Order
    form_class = OrderForm
    extra_context = {'page_title': 'Create Order'}
    template_name = 'order/create_order.html'

    def get_success_url(self):
        return self.request.session.get('checkout_url')

    def form_valid(self, form):
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
                set_payment_status_check_schedule(order_id=self.object.pk, stripe_session_id=stripe_session['id'])

                return super().form_valid(form)
            else:
                ValidationError('Select items for your order')
