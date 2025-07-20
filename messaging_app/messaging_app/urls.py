from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define the schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Messaging App API",
        default_version='v1',
        description="API documentation for the Django Messaging Application.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@messagingapp.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes for chats (conversations and messages)
    path('api/v1/chats/', include('chats.urls')),

    # Django REST Framework login/logout views
    path('api-auth/', include('rest_framework.urls')),

    # Swagger/OpenAPI docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
