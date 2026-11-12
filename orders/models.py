from django.db import models

# Create your models here.
class Table(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=4)
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return self.name