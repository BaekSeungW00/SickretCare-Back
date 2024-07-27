from rest_framework import serializers
from .models import *

class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = '__all__'
        extra_kwargs = {
            'interval': {'required': False}
        }
        
class PushSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alarm
        fields = '__all__'