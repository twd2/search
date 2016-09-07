from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^search$', views.search, name='search'),
    url(r'^search2$', views.search2, name='search2'),
]
