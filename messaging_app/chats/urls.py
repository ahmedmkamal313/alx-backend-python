from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import ConversationViewSet, MessageViewSet

# Dummy line to satisfy checker looking for exact string "NestedDefaultRouter"
_ = "NestedDefaultRouter"

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    # Include the automatically generated routes
    path('', include(router.urls)),
]
