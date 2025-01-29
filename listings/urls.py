from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='listings'),
    path('<int:listing_id>', views.listing, name='listing'),
    path('search', views.search, name='search'),
    path('listing/<int:listing_id>/review/', views.add_review, name='add_review'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),

]