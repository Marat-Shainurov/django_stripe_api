import json

from django.http import Http404, JsonResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect

from item.models import Item
from order.service import ProjectStripeSession


def get_item(request, item_id):
    """
    View to display item details and handle the purchase request.
    If the request method is POST and contains 'buy_item', it initiates a purchase
    by making a GET request to the 'buy_item' view. The user is then redirected to
    the Stripe Checkout URL for completing the purchase.

    :param request: HTTP request object
    :param item_id: ID of the item to be displayed and purchased.
    :return: A rendered HTML page displaying item details or a redirect to the Stripe Checkout URL.
    """
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
        context = {'item': item, 'page_title': 'Buy Item'}
        return render(request, 'item/get_item.html', context)


def buy_item(request, item_id):
    """
    View to initiate the purchase process for a specific item (item.Item instance).
    If the request method is GET, it creates a new Stripe session for the specified
    item, retrieves the session ID and Checkout URL, and returns them as JSON.

    :param request: HTTP request object
    :param item_id: ID of the item to be purchased.
    :return: A JSON response containing the Stripe session ID and Checkout URL.
    """
    if request.method == 'GET':
        item = get_object_or_404(Item, pk=item_id)
        project_stripe_obj = ProjectStripeSession(items=[item])
        stripe_session = project_stripe_obj.make_session()
        response_data = {'stripe_session_id': stripe_session['id'], 'checkout_url': stripe_session['url']}
        return JsonResponse(response_data)
