from rest_framework import serializers
from .models import *

class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = '__all__'
        extra_kwargs = {
            'interval': {'required': False}
        }
        
class AlarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False}
        }
        
class TimerPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimerPush
        fields = '__all__'
        
class AlarmPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmPush
        fields = '__all__'