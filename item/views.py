import json

from django.http import Http404, JsonResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect

from item.models import Item
from item.service import ProjectStripeSession


def get_item(request, item_id):
    if request.method == 'POST':
        if 'buy_item' in request.POST:
            buy_request = HttpRequest()
            buy_request.method = 'GET'
            buy_request.GET = {'item_id': item_id}
            buy_item_response = buy_item(buy_request, item_id)
            response_data = json.loads(buy_item_response.content)
            checkout_url = response_data.get('checkout_url')
            return redirect(checkout_url)
    else:
        try:
            item = get_object_or_404(Item, pk=item_id)
        except Http404:
            return {'detail': 'Not found'}
        context = {'item': item}
        return render(request, 'item/get_item.html', context)


def buy_item(request, item_id):
    if request.method == 'GET':
        item = get_object_or_404(Item, pk=item_id)
        project_stripe_obj = ProjectStripeSession(obj_name=item, obj_price=item.price, obj_currency=item.currency)
        stripe_session = project_stripe_obj.make_session()
        response_data = {'stripe_session_id': stripe_session['id'], 'checkout_url': stripe_session['url']}
        return JsonResponse(response_data)

# todo: finish the view and template,
#  add the stripe service methods, create
#  the order view/url/template + stripe + discounts + tax
