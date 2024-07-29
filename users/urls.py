from django.urls import path

from . import views

urlpatterns = [
    path('', views.user_retrieve_update_destroy_api_view, name='user-retrieve-update-destroy-api-view'),
    path('signup/', views.UserCreateAPIView.as_view(), name='user-signup'),
    path('login/', views.login_api_view, name='user-login'),
    path('logout/', views.logout_api_view, name='user-logout'),
    path('refresh/', views.refresh_api_view, name='user-refresh'),
    path('reset_pw/', views.reset_pw_api_view, name='user-reset-pw'),
]