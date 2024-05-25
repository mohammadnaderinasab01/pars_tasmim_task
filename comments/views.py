from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import CommentCreateOrUpdateOrDeleteSerializer, CommentReadSerializer
from rest_framework.permissions import AllowAny
from authentication.permission import UserAccessPermission
from datetime import datetime
from rest_framework import status
from advertisements.models import Advertisement
from users.models import User
from .models import Comment
import json


class CommentViewSet(GenericViewSet):
    queryset = Comment.objects.all()
    
    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            return CommentCreateOrUpdateOrDeleteSerializer
        elif self.request.method == 'GET':
            return CommentReadSerializer
        return CommentReadSerializer
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return [UserAccessPermission(),]
        else:
            return [AllowAny(), ]

    def create(self, request):
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            
            try:
                if str(request.user.id) == request.data['user_id']:
                    return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_400_BAD_REQUEST,
                            'message': 'شما نمی توانید برای تبلیغاتی که خودتان ثبت کرده‌اید، کامنت بگذارید'
                        }],
                        # 'result': serializer.data,
                        'resultStatus': 1
                    }, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            
            # check that not both comment_id and advertisement_id has been sent
            if body.get('advertisement_id') != None and body.get('advertisement_id') != '' and body.get('comment_id') != None and body.get('comment_id') != '':
                return Response(data='you cannot send comment_id and advertisement_id at the same time', status=status.HTTP_400_BAD_REQUEST)

            user_advertisements = User.objects.get(pk=body.get('user_id')).comment_set.all()

            for adv in user_advertisements:
                if str(adv.advertisement_id.id) == body.get('advertisement_id'):
                    return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_400_BAD_REQUEST,
                            'message': 'شما نمی توانید بیش از یکبار روی یک تبلیغ کامنت بگذارید'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=status.HTTP_400_BAD_REQUEST)

            # serializing the comment model
            serializer = CommentCreateOrUpdateOrDeleteSerializer(data=request.data)
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
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': e
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
            parameters=[
                OpenApiParameter(name='advertisement_id', type=OpenApiTypes.UUID),
                OpenApiParameter(name='min_created_at', type=OpenApiTypes.DATETIME),
                OpenApiParameter(name='max_created_at', type=OpenApiTypes.DATETIME),
                OpenApiParameter(name='order_by_created_at', type=OpenApiTypes.STR),
                OpenApiParameter(name='search_phrase', type=OpenApiTypes.STR),
            ]
    )
    def list(self, request):
        try:
            queryset = Comment.objects.all()

            # filter based on advertisement id
            if request.GET.get('advertisement_id') != None and request.GET.get('advertisement_id') != '' and (request.GET.get('comment_id') == None or request.GET.get('comment_id') == ''):
                queryset = queryset.filter(advertisement_id__id__contains=request.GET.get('advertisement_id'))

            # filter based on min & max creation time
            if request.GET.get('min_created_at') != None and request.GET.get('min_created_at') != '' and request.GET.get('max_created_at') != None and request.GET.get('max_created_at') != '':
                try:
                    if datetime.strptime(request.GET.get('min_created_at'), '%Y-%m-%dT%H:%M:%S.000Z') > datetime.strptime(request.GET.get('max_created_at'), '%Y-%m-%dT%H:%M:%S.000Z'):
                        return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_400_BAD_REQUEST,
                                'message': 'مقدار قدیمی‌ترین تاریخ نباید بزرگتر از جدیدترین تاریخ باشد.'
                            }],
                            'result': None,
                            'resultStatus': 1
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)
                    return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_400_BAD_REQUEST,
                                'message': 'فرمت تاریخ تنها میتواند به اینصورت باشد: Y-m-dTH-M-S'
                            }],
                            'result': None,
                            'resultStatus': 1
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('min_created_at') != None and request.GET.get('min_created_at') != '':
                try:
                    date_check = bool(datetime.strptime(request.GET.get('min_created_at'), '%Y-%m-%dT%H:%M:%S.000Z'))
                    queryset = queryset.filter(created_at__gte=request.GET.get('min_created_at'))
                except Exception as e:
                    print(e)
                    return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_400_BAD_REQUEST,
                                'message': 'فرمت تاریخ تنها میتواند به اینصورت باشد: Y-m-dTH-M-SZ'
                            }],
                            'result': None,
                            'resultStatus': 1
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            if request.GET.get('max_created_at') != None and request.GET.get('max_created_at') != '':
                try:
                    date_check = bool(datetime.strptime(request.GET.get('max_created_at'), '%Y-%m-%dT%H:%M:%S.000Z'))
                    queryset = queryset.filter(created_at__lte=request.GET.get('max_created_at'))
                except Exception as e:
                    return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_400_BAD_REQUEST,
                                'message': 'فرمت تاریخ تنها میتواند به اینصورت باشد: Y-m-dTH-M-SZ'
                            }],
                            'result': None,
                            'resultStatus': 1
                        }, status=status.HTTP_400_BAD_REQUEST)

            # sort by vote total and creation time
            if request.GET.get('order_by_created_at') != None and request.GET.get('order_by_created_at') != '' and request.GET.get('order_by_vote_total') != None and request.GET.get('order_by_vote_total') != '':
                return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_400_BAD_REQUEST,
                                'message': 'در یک زمان، فقط یکی از مرتب‌سازها می‌توانند فعال باشند'
                            }],
                            'result': None,
                            'resultStatus': 1
                        }, status=status.HTTP_400_BAD_REQUEST)

            if request.GET.get('order_by_created_at') != None and request.GET.get('order_by_created_at') != '':
                if request.GET.get('order_by_created_at') == 'asc':
                    queryset = queryset.order_by('created_at')
                elif request.GET.get('order_by_created_at') == 'desc':
                    queryset = queryset.order_by('-created_at')
                else:
                    queryset = None

            if request.GET.get('search_phrase') != None and request.GET.get('search_phrase') != '':
                queryset = queryset.filter(content__icontains=request.GET.get('search_phrase'))

            serializer = CommentReadSerializer(queryset, many=True)
            return Response({
                            'validationMessage': [{
                                'statusCode': status.HTTP_200_OK,
                                'message': 'اطلاعات با موفقیت دریافت شد'
                            }],
                            'result': serializer.data,
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
            comment = Comment.objects.get(pk=pk)
            serializer = CommentReadSerializer(instance=comment)
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_200_OK,
                            'message': 'اطلاعات با موفقیت دریافت شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
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


    def update(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)

            if request.data.get('user_id') != None and request.data['user_id'] != '':
                comment.user_id = request.data['user_id']

            if request.data.get('advertisement_id') != None and request.data['advertisement_id'] != '':
                comment.advertisement_id = request.data['advertisement_id']

            if request.data.get('content') != None and request.data['content'] != '':
                comment.content = request.data['content']
            
            comment.save()
            serializer = CommentCreateOrUpdateOrDeleteSerializer(instance=comment)
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_202_ACCEPTED,
                            'message': 'اطلاعات با موفقیت بروزرسانی شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_202_ACCEPTED)
        except Comment.DoesNotExist:
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
            comment = Comment.objects.get(pk=pk)
            serializer = CommentCreateOrUpdateOrDeleteSerializer(instance=comment)
            comment.delete()
            return Response({
                        'validationMessage': [{
                            'statusCode': status.HTTP_204_NO_CONTENT,
                            'message': 'اطلاعات با موفقیت حذف شد'
                        }],
                        'result': serializer.data,
                        'resultStatus': 0
                    }, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
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