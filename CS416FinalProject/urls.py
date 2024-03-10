"""
URL configuration for CS416FinalProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from TM import views
from TM.models import LikedEventListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tm/',views.tm_view, name="ticketmaster_view"),
    path('home/', views.home_page, name="home"),
    path('', views.home_page),
    path('login/',views.login_page, name="login"),
    path('register/',views.register_view, name ="register"),
    path('get_events/', views.get_events, name='get_events'),
    path('like_event/', views.like_event, name='like_event'),
    path('liked_events/', LikedEventListView.as_view(), name='liked_events'),
    path('remove_from_liked/<int:event_id>/', views.remove_from_liked, name='remove_from_liked'),
    path('audio/', views.audio, name='audio'),
]
