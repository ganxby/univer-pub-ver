from django.urls import path
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token
)

from . import views

urlpatterns = [
    path('test/', views.get_current_user),

    path('token-auth/', obtain_jwt_token),
    path('token-refresh/', refresh_jwt_token),
    path('token-verify/', verify_jwt_token),

    path('login/', views.check_valid_data)
]