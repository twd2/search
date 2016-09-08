from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^search$', views.search, name='search'),
    url(r'^page/(?P<pk>\d+)$', views.PageView.as_view(), name='page'),
    url(r'^page/(?P<pk>\d+)/json$', views.page_json, name='page_json'),
]
