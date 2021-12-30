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
from django.urls import path, re_path
from ga.views import view
from ga.subviews.handlers import handler404_base
from django.conf.urls import include

urlpatterns = [
    # auth
    re_path(r'^', include('django.contrib.auth.urls')),  # redirect all to login if not logged in
    path('accounts/', include('django.contrib.auth.urls')),  # login page
    # ga
    re_path(r'^$', view),
    path('<str:a>', view),
    path('<str:a>/', view),
    path('<str:a>/<str:b>', view),
    path('<str:a>/<str:b>/', view),
    path('<str:a>/<str:b>/<str:c>', view),
    path('<str:a>/<str:b>/<str:c>/', view),
    path('<str:a>/<str:b>/<str:c>/<str:d>', view),
    path('<str:a>/<str:b>/<str:c>/<str:d>/', view),
    path('<str:a>/<str:b>/<str:c>/<str:d>/<str:e>', view),
    path('<str:a>/<str:b>/<str:c>/<str:d>/<str:e>/', view),

    # fallback
    re_path(r'^', handler404_base),
]
