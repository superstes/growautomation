"""base URL Configuration

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
from django.conf.urls import url
from ga.views import view_config, view_home, view_system, handler404, view_logout
from django.conf.urls import include

urlpatterns = [
    # mgmt
    # url(r'^admin/', admin.site.urls),
    # auth
    url('^', include('django.contrib.auth.urls')),  # redirect all to login if not logged in
    path('accounts/', include('django.contrib.auth.urls')),  # login page
    path('logout/', view_logout),  # logout page
    # ga
    #   config
    path('config/<str:action>/<str:typ>', view_config),
    path('config/<str:action>/<str:typ>/', view_config),
    path('config/<str:action>/<str:typ>/<int:uid>', view_config),
    path('config/<str:action>/<str:typ>/<int:uid>/', view_config),
    path('config/<str:action>/<str:typ>/<str:sub_type>', view_config),
    path('config/<str:action>/<str:typ>/<str:sub_type>/', view_config),
    path('config/<str:action>/<str:typ>/<str:sub_type>/<int:uid>', view_config),
    path('config/<str:action>/<str:typ>/<str:sub_type>/<int:uid>/', view_config),
    #   system
    path('system/<str:typ>/<str:sub_type>/', view_system),
    path('system/<str:typ>/', view_system),
    #   data
    path('data/<str:typ>/', view_system),
    #   defaults
    url(r'^home/?|^main/?|^/?$', view_home),
    url(r'^$', view_home),
    url(r'^denied/?$', view_home),
    url(r'^', handler404),
]
