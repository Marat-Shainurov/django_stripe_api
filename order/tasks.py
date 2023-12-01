import json
import pytz
from datetime import datetime

from celery import shared_task
from django.shortcuts import get_object_or_404
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from config import settings
from order.models import Order
from order.service import ProjectStripeSession


@shared_task
def disable_payment_status_check(order_id: str) -> None:
    """Sets the 'task.enable' field to False"""
    task = PeriodicTask.objects.get(name=f'Payment status check for Order {order_id}')
    task.enabled = False
    task.save()


@shared_task
def set_pay_status(order_id: str, stripe_session_id: str) -> None:
    """
    Task called periodically to check the Stripe Checkout Session payment status.
    Sets 'paid' as the Order instance's payment_status field value if the payment has been done.

    :param order_id: id of the Order instance expected to be paid.
    :param stripe_session_id: the Stripe Checkout Session id which payment status should be checked
    """
    if ProjectStripeSession.get_payment_status(stripe_session_id):
        order = get_object_or_404(Order, pk=order_id)
        order.payment_status = 'paid'
        order.save()
        disable_payment_status_check.delay(order_id)


def set_payment_status_check_schedule(order_id, stripe_session_id) -> None:
    """
    Sets the set_pay_status periodic task schedule.

    :param order_id: id of the Order instance expected to be paid.
    :param stripe_session_id: the Stripe Checkout Session id which payment status should be checked
    """
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=2,
        period=IntervalSchedule.MINUTES,
    )
    actual_time = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))

    PeriodicTask.objects.create(
        interval=schedule,
        start_time=actual_time,
        name=f'Payment status check for Order {order_id}',
        task='order.tasks.set_pay_status',
        args=json.dumps([order_id, stripe_session_id]),
        kwargs={},
    )
