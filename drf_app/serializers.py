from rest_framework import serializers
from .models import Info


class Infoserializer(serializers.ModelSerializer):

    class Meta:
        model = Info
        # fields = ['name', 'address']
        fields= "__all__"



















# class InfoSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Info
#         fields = "__all__"