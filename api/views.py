from django.http import HttpResponse
from django.shortcuts import render
from api.search import views
import requests
# Create your views here.


def aboutPage(request):
    dict={}
    annotated_article_number = views.findArticleNumber()
    dict["article_number"]=annotated_article_number

    annotation_number= views.findAnnotationNumber()
    dict["annotation_number"]=annotation_number


    return render(request, 'html/about.html',{'metrics_data': dict})
