from django.db import models


class Telegram(models.Model):
    telegram_id = models.IntegerField(default=0)
    first_name = models.CharField(max_length=255,blank=True,null=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    username = models.CharField(max_length=255,blank=True,null=True)
    phone = models.CharField(max_length=255,blank=True,null=True)
    is_admin = models.BooleanField(default=False)
    step = models.IntegerField(default=1)
    text = models.CharField(max_length=255,blank=True,null=True)


    def __str__(self):
        return str(self.pk)