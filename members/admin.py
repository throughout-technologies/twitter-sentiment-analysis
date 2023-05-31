from django.contrib import admin
from members.models import Sentiment
 
@admin.register(Sentiment)
# Register your models here.
class SentimentAdmin(admin.ModelAdmin):
    list_display=['id']
   