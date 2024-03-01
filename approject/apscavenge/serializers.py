from rest_framework import serializers
from .models import Seizure, InfoHistory, PasswordHash, AgentStatus

class CentralHeartbeatSerializer(serializers.Serializer):
    area = serializers.CharField(max_length=64)

    #def validate_area(self, value):
    #    if len(value) < 3:
    #        raise serializers.ValidationError("Area should have at least 3 characters.")
    #    return value

class SeizureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seizure
        fields = ['email']

class InfoHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoHistory
        fields = ['id', 'user_type', 'user_info', 'capture_time', 'area', 'seizure_email']

class PasswordHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordHash
        fields = ['id', 'asleap', 'jtr', 'hashcat', 'info_history_id']

class AgentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStatus
        fields = ['id', 'ip', 'token', 'area', 'is_online', 'is_attacking', 'last_heartbeat']