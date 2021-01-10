"""mentisparchment_docker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from api.search import views
from django.conf import settings
import os
from django.views.static import serve as staticserve
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', views.startSearch, name='search'),
    path('annotations/<int:annotationId>', views.annotations, name='annotations'),
    path('', views.page),
    path('summary-page/', views.summaryPage, name='summaryPage'),
    path('articlenumbers/', views.findStoredArticleNumber, name='storedArticles'),
]
