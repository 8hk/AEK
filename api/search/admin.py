from django.contrib import admin

# Register your models here.
from api.search.models import AnnotatedArticle

admin.site.register(AnnotatedArticle)