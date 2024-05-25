from rest_framework import serializers
from .models import Comment


class CommentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 1

class CommentReadSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 1

class CommentCreateOrUpdateOrDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('id', 'created_at')