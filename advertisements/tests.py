from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.serializers import UserSerializer, UserLoginSerializer
from .serializers import AdvertisementCreateOrUpdateOrDeleteSerializer
from rest_framework.test import force_authenticate
import json
import base64


class UserLoginAPITests(APITestCase):

    def setUp(self):

        self.user_dict = {
            'first_name': 'mohammad',
            'last_name': 'naderinasab',
            'email': 'mohammad_naderinasab@yahoo.com',
            'password': 'mohammad_password',
        }

        user_serializer = UserSerializer(data=self.user_dict)
        if user_serializer.is_valid():
            user_serializer.save()


    def test_create_advertisement(self):
        """
        Ensure we can login with a valid user.
        """
        
        url = reverse('login')
        data = {
            "email": self.user_dict['email'],
            "password": self.user_dict['password'],
        }
        response = self.client.post(url, data, format='json')
        
        authenticated_user = authenticate(username=self.user_dict['email'], password=self.user_dict['password'])
        if authenticated_user:
            serializer = UserLoginSerializer(authenticated_user)
        
        url = '/advertisements/'
        test_advertisement = {
            'title': 'title for test advertisement creation',
            'content': 'content for test advertisement creation',
            'user_id': authenticated_user.id
        }

        self.client.defaults['HTTP_AUTHORIZATION'] = f'Basic {json.loads(response.content)["token"]}'
        self.client.defaults['Cookie'] = "csrftoken=GUG1DyWTqtLkYOFO98xV9cLMcbJcPVNL"

        response = self.client.post(url, test_advertisement, format='json', Authorization=f'Bearer {json.loads(response.content)["token"]}')

        serializer = AdvertisementCreateOrUpdateOrDeleteSerializer(data=test_advertisement)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_invalid_credentials(self):
        """
        Ensure we can't login with invalid credentials.
        """
        url = reverse('login')
        data = {
            "email": self.user_dict['email'],
            "password": 'mohammad_password',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
