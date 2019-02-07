from django.db import models


class Product(models.Model):
    category = models.ForeignKey('category.SubCategory',on_delete=models.CASCADE)
    photo_url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    description = models.TextField(max_length=1500)

    def __str__(self):
        return str(self.category) + '-' + self.name