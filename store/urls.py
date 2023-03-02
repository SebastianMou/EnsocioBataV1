from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('seller_register/', views.seller_register, name='seller_register'),
    path('buyer_register/', views.buyer_register, name='buyer_register'),
    path('create_post/', views.create_post, name='create_post'),
    path('profile/', views.profile, name='profile'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),
    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
]