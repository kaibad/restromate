from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save

from .models import Order,OrderHistory

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
