from django.urls import path
from .api_views import BookListCreateView, BookRetrieveUpdateDestroyView, UserProfileView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,  # Optional: if you want an endpoint to verify tokens
)

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name='api-books-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='api-book-detail'),
    path('profile/',UserProfileView.as_view(),name='api-user-profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),#used to refresh access tokens
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), # Optional
    path('logout/', LogoutView.as_view(), name='auth_logout_api'), # New logout endpoint
]
