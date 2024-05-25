from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.serializers import UserSerializer, UserLoginSerializer, UserSignupSerializerRequest, UserLoginSerializerRequest
from drf_spectacular.utils import extend_schema


class RegistrationView(APIView):
    @extend_schema(
        request=UserSignupSerializerRequest
    )
    def post(self, request):
        try:
            print('1')
            serializer = UserSerializer(data=request.data)
            print('2')
            if serializer.is_valid():
                print('2,4')
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print('3')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        request=UserLoginSerializerRequest
    )
    def post(self, request):
        username = request.data.get('email', None)
        password = request.data.get('password', None)

        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user:
            serializer = UserLoginSerializer(authenticated_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Invalid Credentials", status=status.HTTP_401_UNAUTHORIZED)