from django.urls import path
from .views import RegisterView

from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LogoutView, ProfileView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/', ProfileView.as_view(), name='profile'),
]
