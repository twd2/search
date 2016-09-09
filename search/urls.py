from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^search$', views.search, name='search'),
    url(r'^advanced', views.advanced, name='advanced'),
    url(r'^page/(?P<pk>\d+)$', views.PageView.as_view(), name='page'),
    url(r'^page/(?P<pk>\d+)/json$', views.page_json, name='page_json'),
    url(r'^page/(?P<pk>\d+)/go$', views.page_go, name='page_go'),
    url(r'^cache$', views.cache, name='cache'),
    url(r'^cache/clear$', views.cache_clear, name='cache_clear'),
]
