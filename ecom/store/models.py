from django.db import models
import datetime


class Category(models.Models):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Customer(models.Models):
    pass

class Product(models.Models):
    pass

class Order(models.Models):
    pass
