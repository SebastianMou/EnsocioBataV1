from django.urls import path
from . import views
from django.contrib.auth import views as auth_views #import this

urlpatterns = [
    path('', views.home, name='home'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('seller_register/', views.seller_register, name='seller_register'),
    path('buyer_register/', views.buyer_register, name='buyer_register'),
    path('create_post/', views.create_post, name='create_post'),
    path('profile/', views.profile, name='profile'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),
    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('category_list/<int:pk>', views.category_list, name='category_list'),

    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html', success_url='/password_changed/'), name='password_change'),
    path('password_changed/', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_changed.html'), name='password_changed'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),      
]