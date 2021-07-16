from rest_framework import serializers


class CourierSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    courier_type = serializers.CharField()
    regions = serializers.ListField(child=serializers.IntegerField())
    working_hours = serializers.ListField(child=serializers.CharField())
