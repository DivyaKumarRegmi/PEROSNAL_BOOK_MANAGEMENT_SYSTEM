from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from mozilla_django_oidc import views as oidc_views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.list_books, name='list_books'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Auth and Profile
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.smart_logout, name='logout'), # Points to our smart handler
    #path('oidc/logout/', oidc_views.OIDCLogoutView.as_view(), name='oidc_logout'), # The library's logout view
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Keycloak URLs for mozilla-django-oidc
   path('oidc/', include('mozilla_django_oidc.urls')),

    # Account activation
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Password reset
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
