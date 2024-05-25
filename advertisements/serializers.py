from rest_framework import serializers
from .models import Advertisement
from comments.serializers import CommentReadSerializer


class AdvertisementCreateOrUpdateOrDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        exclude = ('id', )

class AdvertisementCreateSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        exclude = ('id', )

class AdvertisementUpdateOrDeleteSerializerRequest(serializers.ModelSerializer):
    title = serializers.CharField(max_length=300, required=False)
    content = serializers.CharField(max_length=None, required=False)
    # user_id = serializers.CharField(max_length=300, required=False)
    class Meta:
        model = Advertisement
        exclude = ('id', 'user_id')

class AdvertisementReadSerializer(serializers.ModelSerializer):
    comments = CommentReadSerializer(many=True, read_only=True, source='comment_set')
    class Meta:
        model = Advertisement
        fields = '__all__'
        depth = 1