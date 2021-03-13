from django.db import models

# Create your models here.
class AbstractTimeStamp(models.Model):
    """ TimeStamp Model"""
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True