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
    hm = serializers.SerializerMethodField()
    class Meta:
        model = Alarm
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},
            'hm': {'read_only': True}
        }
    
    def get_hm(self, obj):
        return str(obj.time)[:5]
        
class TimerPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimerPush
        fields = '__all__'
        
class AlarmPushSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmPush
        fields = '__all__'