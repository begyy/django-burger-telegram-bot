from django.db import models


class Order(models.Model):
    STATUS_CHOICE = (('new','new'),('processing','processing'),('finished','finished'),('cancel','cancel'))
    user = models.ForeignKey('telegram_users.Telegram',on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICE,max_length=255,default='new')
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=255,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product',on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.product)