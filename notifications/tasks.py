from firebase_admin import credentials, messaging, initialize_app
from django.utils import timezone
from datetime import timedelta, time
from celery import shared_task
from .models import *

# 서비스 계정 키 파일 경로
cred = credentials.Certificate("team6-back-firebase-adminsdk-470ya-e723c42217.json")

# Firebase 초기화
initialize_app(cred)

@shared_task
def check_and_send_timer_pushes():
    now = timezone.now()
    timer_pushes = TimerPush.objects.all()
    for timer_push in timer_pushes:
        if timer_push.created_at + timedelta(minutes=timer_push.timer.interval) <= now:
            send_timer_push(timer_push)
            timer_push.delete()

@shared_task 
def check_and_send_alarm_pushes():
    now = timezone.now()
    alarm_pushes = AlarmPush.objects.all()
    for alarm_push in alarm_pushes:
        if alarm_push.time <= now:
            send_alarm_push(alarm_push)
            
            next_alarm_push = AlarmPush.objects.create(
                title=alarm_push.title, 
                time=(alarm_push.time + timedelta(days=1)), 
                alarm=alarm_push.alarm
                )
            
            next_alarm_push.save()
            alarm_push.delete()
  
def send_timer_push(push):
    fcm_token=push.timer.user.fcm_token
    message = messaging.Message(
        data = {
            "title": "Sickret Care 타이머 알림",
            "body": "지정한 시간이 다 되었습니다!",
            "url": "" # 메인 페이지 url
        },
        token=fcm_token
    )
    # 푸시 알림 메시지 전송
    response = messaging.send(message)
    print('Successfully sent push message:', response)

def send_alarm_push(push):
    fcm_token=push.alarm.user.fcm_token
    message = messaging.Message(
        data = {
            "title": "Sickret Care Alarm 알림",
            "body": push.title,
            "url": "" # 메인 페이지 url
        },
        token=fcm_token
    )
    # 푸시 알림 메시지 전송
    response = messaging.send(message)
    print('Successfully sent alarm message:', response)