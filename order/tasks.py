import json
import pytz
from datetime import datetime, timedelta

from celery import shared_task
from django.shortcuts import get_object_or_404
from django_celery_beat.models import IntervalSchedule, PeriodicTask, ClockedSchedule

from config import settings
from order.models import Order
from order.service import ProjectStripeSession


@shared_task
def disable_payment_status_check(order_id: str) -> None:
    """
    Sets the 'task.enable' field to False if the order has been paid, and there is no need to check its
    payment status again.

    :param order_id: id of the paid Order instance.
    """
    task = PeriodicTask.objects.get(name=f'Payment status check for Order {order_id}')
    task.enabled = False
    task.save()


@shared_task
def set_payment_status(order_id: str, stripe_session_id: str) -> None:
    """
    Task is called periodically to check the Stripe Checkout Session payment status.
    Sets 'paid' as the Order instance's payment_status field value if the payment has been done.

    :param order_id: id of the Order instance expected to be paid.
    :param stripe_session_id: the Stripe Checkout Session id which payment status should be checked
    """
    if ProjectStripeSession.get_payment_status(stripe_session_id):
        order = get_object_or_404(Order, pk=order_id)
        order.payment_status = 'paid'
        order.save()
        disable_payment_status_check.delay(order_id)


@shared_task()
def set_payment_status_check_schedule(order_id, stripe_session_id) -> None:
    """
    Sets the set_payment_status periodic task schedule.

    :param order_id: id of the Order instance expected to be paid.
    :param stripe_session_id: the Stripe Checkout Session id which payment status should be checked
    """
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=2,
        period=IntervalSchedule.MINUTES,
    )
    start_time = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + timedelta(seconds=120)

    PeriodicTask.objects.create(
        interval=schedule,
        start_time=start_time,
        name=f'Payment status check for Order {order_id}',
        task='order.tasks.set_payment_status',
        args=json.dumps([order_id, stripe_session_id]),
        kwargs={}
    )


@shared_task
def set_disabler_schedule(order_id: str):
    """
    Sets a new ClockedSchedule schedule for one-off task to disable the set_payment_status periodic task.
    Expiration time - 30 minutes from the first payment status check.
    Aligns with the expires_at option of the Stripe Checkout Session configured in order.service.ProjectStripeSession.
    Disables the payment status check task after 30 minutes from the start_time of the set_payment_status_check_schedule

    :param order_id: the order.Order instance id, which pyament status check is being disabled.
    :return:
    """
    now = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    disable_at = now + timedelta(seconds=1800)
    schedule, created = ClockedSchedule.objects.get_or_create(
        clocked_time=disable_at
    )
    PeriodicTask.objects.create(
        clocked=schedule,
        one_off=True,
        name=f'Disables payment status check for Order {order_id}',
        task='order.tasks.disable_payment_status_check',
        args=json.dumps([order_id, ]),
        kwargs={},
    )
