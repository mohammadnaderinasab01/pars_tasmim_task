# from django.contrib.auth.models import User
from users.models import User
from rest_framework import serializers
# from advertisements.serializers import AdvertisementReadSerializer
from helpers.jwt_helper import JWTHelper


class UserSerializer(serializers.ModelSerializer):
    # advertisements = AdvertisementReadSerializer(many=True, read_only=True, source='advertisement_set')
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('token',)

    def get_token(self, user):
        user = JWTHelper.encode_token(user)
        return user

class UserSignupSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
    
class UserLoginSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']