from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('seller_register/SVZOMGHDICY27X5-YWB5LZF2O3KXPSI-KI45BDEYRSQ0LFT-ELOWF93S846ATVQ/', views.seller_register, name='seller_register'),
    path('buyer_register/', views.buyer_register, name='buyer_register'),
    path('user_login/', views.user_login, name='user_login'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('profile/', views.profile, name='profile'),
    path('visible_profile/<str:username>/', views.visible_profile, name='visible_profile'),
    # Controlling post
    path('create_post/', views.create_post, name='create_post'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),
    path('comment_delete/<int:pk>/', views.comment_delete, name='comment_delete'),
    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('category_list/<int:pk>', views.category_list, name='category_list'),
    # Stripe Payment connection
    path('create_checkout_session/<int:pk>/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout_success/', views.checkout_success, name='checkout_success'),
    path('checkout_cancel/', views.checkout_cancel, name='checkout_cancel'),
    # activación de la cuenta de usuario por correo electrónico
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    # path('activate_buyer/<uidb64>/<token>', views.activate_buyer, name='activate_buyer'),

    # User change password from account 
    path('change_password/', login_required(auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html', success_url='/password_changed/')), name='password_change'),
    path('password_changed/', login_required(auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_changed.html')), name='password_changed'),    
    # Forgoten password
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),      
]