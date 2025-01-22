from django.contrib import admin
from django.urls import path
from search.views import *
from debug_toolbar.toolbar import debug_toolbar_urls
urlpatterns = [
    path('', index),
]+ debug_toolbar_urls()
