from django.views import generic

from order.service import ProjectStripeSession
from order.forms import OrderForm
from order.models import Order


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
            items = form.cleaned_data['items']
            discount = form.cleaned_data['discount']
            tax = form.cleaned_data['tax']
            project_stripe_obj = ProjectStripeSession(
                items=items,
                discount=discount,
                tax=tax)
            stripe_session = project_stripe_obj.make_session()
            self.request.session['checkout_url'] = stripe_session['url']

            return super().form_valid(form)
