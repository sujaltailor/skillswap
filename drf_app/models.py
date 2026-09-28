from django.db import models

# Create your models here.
class Info(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=150, null=False)