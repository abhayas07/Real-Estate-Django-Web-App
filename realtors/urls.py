from django.urls import path
from . import views

urlpatterns = [
    
    path('login/', views.realtor_login, name='realtor_login'),
    path('register/', views.realtor_register, name='realtor_register'),
]
