from django.urls import path   
from members.views import sentimentAnalysis,index

urlpatterns = [
    path('',index,name='homepage'),
    path('show',sentimentAnalysis,name="analysispage"),
]
 