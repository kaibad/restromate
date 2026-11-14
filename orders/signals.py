from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save

from .models import Order,OrderHistory, OrderItem

from django.db.models import Count, Q

# o1 = = Order.objects.all()
#
#o1.status = "r"
#emit -> pre_save
# instace -> order._old_status = o1.status
#o1.save()
# emit -> post_save


@receiver(pre_save,sender=Order)
def remember_old_status(sender,instance,**kwargs):
    if instance._state.adding:
        # brand new order, nothing in the database yet
        instance._old_status = None
    else:
        instance._old_status = (
            Order.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        )

@receiver(post_save,sender=Order)
def create_order_history(sender, instance, created, **kwargs):
    if created or instance._old_status != instance.status:
        OrderHistory.objects.create(order=instance, status=instance.status)

@receiver(post_save,sender=OrderItem)
def handle_auto_order_status_update(sender, instance, **kwargs):
    order = instance.order

    # A billed order is finished, so item changes no longer affect it
    if order.status == Order.ORDER_STATUS.BILLED:
        return

    counts = OrderItem.objects.filter(order=order).aggregate(
        total=Count("id"),
        served=Count("id", filter=Q(status=OrderItem.ITEM_STATUS.SERVED)),
    )

    if counts["served"] == 0:
        new_status = Order.ORDER_STATUS.PENDING
    elif counts["served"] == counts["total"]:
        new_status = Order.ORDER_STATUS.SERVED
    else:
        new_status = Order.ORDER_STATUS.PARTIALY_SERVED


    if order.status != new_status:
        order.status = new_status
        order.save(update_fields=["status"])  # the Order signals add the history row

