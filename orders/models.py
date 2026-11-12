
from django.db import models

# Create your models here.
class Table(models.Model):
    name = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=4)
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
         verbose_name_plural = "Categories"

    def __str__(self):
            return self.name


class MenuItem(models.Model):
     category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="items")
     name = models.CharField(max_length=200)
     price = models.PositiveIntegerField()
     description = models.TextField(null=True,blank=True)

     def __str__(self):
            return self.name

