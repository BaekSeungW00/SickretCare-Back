from django.urls import path

from . import views

urlpatterns = [
    path('timer/', views.TimerRetrieveUpdateAPIView.as_view(), name='timer'),
    path('timer/start/', views.start_timer, name='timer-start'),
    path('alarm/', views.AlarmListCreateAPIView.as_view(), name='alarm-list'),
    path('alarm/<int:alarm_id>/', views.AlarmRetrieveUpdateDestroyAPIView.as_view(), name='alarm-retrieve')
]