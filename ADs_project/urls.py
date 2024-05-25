from django.contrib import admin
from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from users.customizations import CustomAdminSite
from django.contrib import admin
from authentication import urls as authentication_urls


# admin.AdminSite = CustomAdminSite
# admin.site.



urlpatterns = [
    path('admin/', admin.site.urls),
    # path('users/', include('users.urls')),
    path('advertisements/', include('advertisements.urls')),
    path('comments/', include('comments.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/auth/', include('authentication.urls')),
    path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)