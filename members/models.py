from django.db import models
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField
 

# Create your models here.

class Sentiment(models.Model):
    data = JSONField( default='')

    def __str__(self):
        return self.data['search']

