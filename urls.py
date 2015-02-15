from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from meshmgr import views

urlpatterns = patterns('',
    url(r'^list_meshes.json$', views.list_meshes ),
    url(r'^list_members.json$', views.list_members ),
)
