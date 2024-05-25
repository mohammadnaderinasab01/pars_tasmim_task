from rest_framework import status
# from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import AdvertisementCreateOrUpdateOrDeleteSerializer, AdvertisementReadSerializer, AdvertisementCreateSerializerRequest, AdvertisementUpdateOrDeleteSerializerRequest
from .models import Advertisement
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from authentication.authentication import UserAuthentication
from authentication.permission import UserAccessPermission
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination


class AdvertisementViewSet(GenericViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    
    queryset = Advertisement.objects.all()
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 3
    pagination_class = PageNumberPagination
    
    parser_classes = (MultiPartParser, )

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            return AdvertisementCreateOrUpdateOrDeleteSerializer
        elif self.request.method == 'GET':
            return AdvertisementReadSerializer
        return AdvertisementReadSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return [UserAccessPermission(),]
        else:
            return [AllowAny(), ]

    # def get_authenticators(self):
    #     if self is not None and self.action is not None:
    #         if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
    #             return [SessionAuthentication, BasicAuthentication]
    #         else:
    #             return []

    @extend_schema(
            request=AdvertisementCreateSerializerRequest
    )
    def create(self, request):
        try:
            serializer = AdvertisementCreateOrUpdateOrDeleteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_201_CREATED,
                            'message': 'اطلاعات با موفقیت ذخیره شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_406_NOT_ACCEPTABLE,
                            'message': e
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)
            


    @extend_schema(
            parameters=[
                # OpenApiParameter(name='tag', type=OpenApiTypes.STR),
                # OpenApiParameter(name='page_num', type=OpenApiTypes.INT),
                # OpenApiParameter(name='page_size', type=OpenApiTypes.INT),
            ]
    )
    def list(self, request):        
        try:
            queryset = self.filter_queryset(Advertisement.objects.order_by('id'))

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = AdvertisementReadSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = AdvertisementReadSerializer(queryset, many=True)

            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_200_OK,
                    'message': 'اطلاعات با موفقیت دریافت شد'
                }],
                'result': serializer.data,
                'totalResult': queryset.count(),
                'resultStatus': 0
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)




    def retrieve(self, request, pk):
        try:
            advertisement = Advertisement.objects.get(pk=pk)
            serializer = AdvertisementReadSerializer(instance=advertisement)
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_200_OK,
                            'message': 'اطلاعات با موفقیت دریافت شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_200_OK)
        except Advertisement.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_404_NOT_FOUND,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
            request=AdvertisementUpdateOrDeleteSerializerRequest
    )
    def update(self, request, pk):
        try:
            advertisement = Advertisement.objects.get(pk=pk)

            if request.data.get('title') != None and request.data['title'] != '':
                advertisement.title = request.data['title']

            if request.data.get('content') != None and request.data['content'] != '':
                advertisement.content = request.data['content']
            
            print(request.user)
            
            if request.user.id != advertisement.user_id.id:
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_400_BAD_REQUEST,
                        'message': 'شما تنها میتوانید تبلیغات خودتان را بروزرسانی کنید'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=status.HTTP_400_BAD_REQUEST)

            advertisement.save()
            serializer = AdvertisementCreateOrUpdateOrDeleteSerializer(instance=advertisement)

            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_202_ACCEPTED,
                            'message': 'اطلاعات با موفقیت بروزرسانی شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_202_ACCEPTED)
        except Advertisement.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_404_NOT_FOUND,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk):
        try:
            
            advertisement = Advertisement.objects.get(pk=pk)

            if request.user.id != advertisement.user_id.id:
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_400_BAD_REQUEST,
                        'message': 'شما تنها میتوانید تبلیغات خودتان را حذف کنید'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = AdvertisementCreateOrUpdateOrDeleteSerializer(instance=advertisement)
            advertisement.delete()

            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_204_NO_CONTENT,
                            'message': 'اطلاعات با موفقیت حذف شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_204_NO_CONTENT)
        except Advertisement.DoesNotExist:
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_404_NOT_FOUND,
                            'message': 'اطلاعات یافت نشد'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)