from django.db import models

class Timer(models.Model):
    interval = models.IntegerField(null=True)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='timer')

class Alarm(models.Model):
    title = models.CharField(max_length=20)
    time = models.TimeField(auto_now=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='pushes')
    