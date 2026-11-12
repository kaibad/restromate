from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    class ROLES_CHOICES(models.TextChoices):
        WAITER = 'w',"Waiter"
        BILLING = 'b',"Billing"
        KITCHEN = 'K',"Kitchen"
        OWNER = 'O',"Owner"

    role = models.CharField(choices=ROLES_CHOICES,max_length=2,default=ROLES_CHOICES.WAITER)