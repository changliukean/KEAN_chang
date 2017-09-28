from django.db import models

# Create your models here.


class user_login_info(models.Model):
    id_user_login_info = models.IntegerField(primary_key=True);
    user_email = models.CharField(max_length=50);
    password = models.CharField(max_length=50);
    authority= models.CharField(max_length=45);
