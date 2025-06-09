from django.db import models

# Create your models here.
# app/models.py
from django.db import models

class Menu(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
