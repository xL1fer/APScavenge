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
        #fields = ['email']
        fields = ['email', 'user_data']

class InfoHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoHistory
        #fields = ['id', 'user_type', 'user_info_id', 'capture_time', 'area', 'seizure_email']
        fields = ['id', 'capture_time', 'area', 'seizure_email']

    def to_internal_value(self, data):
        try:
            data['area'] = data['area'].lower()
        except:
            pass
        return super(InfoHistorySerializer, self).to_internal_value(data)

class PasswordHashSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordHash
        fields = ['id', 'asleap', 'jtr', 'hashcat', 'info_history_id']

class AgentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStatus
        #fields = ['id', 'ip', 'token', 'area', 'alias_name', 'is_online', 'is_attacking', 'is_requesting', 'last_heartbeat']
        fields = ['id', 'ip', 'token', 'area', 'alias_name', 'is_online', 'is_attacking', 'pending_request', 'last_heartbeat']
        
    def to_internal_value(self, data):
        try:
            data['area'] = data['area'].lower()
        except:
            pass
        return super(AgentStatusSerializer, self).to_internal_value(data)