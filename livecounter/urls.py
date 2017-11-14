from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^counters/(?P<counter_id>[^/]+)/$', views.counter, name='counter'),
]
