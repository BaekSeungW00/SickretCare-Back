from django.db import models

class Timer(models.Model):
    interval = models.IntegerField(null=False, default=10)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='timer', null=True)

class Alarm(models.Model):
    title = models.CharField(max_length=20)
    time = models.TimeField(auto_now=False, null=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='pushes', null=True)
    
class TimerPush(models.Model):
    title = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    timer = models.ForeignKey(Timer, on_delete=models.CASCADE, related_name='timer', null=True)
    
class AlarmPush(models.Model):
    title = models.CharField(max_length=20)
    time = models.DateTimeField(auto_created=False, null=True)
    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE, related_name='alarm', null=True)