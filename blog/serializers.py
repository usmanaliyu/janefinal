from django.db import models
from rest_framework import serializers
from rest_framework import fields

from .models import Blog

class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value

class BlogSerializer(serializers.ModelSerializer):
    author = StringSerializer()

    class Meta:
        model = Blog
        fields = "__all__"

    
