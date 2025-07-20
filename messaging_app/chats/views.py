from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
import django_filters.rest_framework # Import the filtering backend
from django_filters import FilterSet, CharFilter, UUIDFilter # Import necessary filter types

from .models import User, Conversation, Message
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer

# Define a FilterSet for Conversation model
class ConversationFilter(FilterSet):
    # Example: Filter conversations by participant user_id
    # This assumes you might want to find conversations involving a specific user
    participant_id = UUIDFilter(field_name='participants__user_id', lookup_expr='exact')

    class Meta:
        model = Conversation
        fields = ['participants', 'created_at'] # 'participants' can be filtered by its ID directly by DRF

# Define a FilterSet for Message model
class MessageFilter(FilterSet):
    # Example: Filter messages by sender username or conversation ID
    sender_username = CharFilter(field_name='sender__username', lookup_expr='icontains')
    conversation_id = UUIDFilter(field_name='conversation__conversation_id', lookup_expr='exact')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_at', 'sender_username', 'conversation_id']


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    Supports listing, retrieving, and creating conversations.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend] # Add filter backend
    filterset_class = ConversationFilter # Specify the filterset class

    def get_queryset(self):
        """
        Optionally restricts the returned conversations to those
        the current user is a participant of.
        """
        user = self.request.user
        if user.is_authenticated:
            # Apply base filter for current user participation
            queryset = self.queryset.filter(participants=user).distinct()
            return queryset
        return self.queryset.none() # Return empty queryset for unauthenticated users

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Expects 'participant_ids' (list of UUID strings) in the request data.
        The creating user is automatically added as a participant.
        """
        # Get participant IDs from request data
        participant_ids = request.data.get('participant_ids', [])
        if not isinstance(participant_ids, list):
            return Response(
                {"detail": "participant_ids must be a list of user UUIDs."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add the current authenticated user's ID to the participants
        current_user_id = str(request.user.user_id)
        if current_user_id not in participant_ids:
            participant_ids.append(current_user_id)

        # Fetch all participant User objects
        try:
            participants = list(User.objects.filter(user_id__in=participant_ids))
            if len(participants) != len(participant_ids):
                # This means some provided IDs were not found
                found_ids = {str(p.user_id) for p in participants}
                missing_ids = [pid for pid in participant_ids if pid not in found_ids]
                return Response(
                    {"detail": f"One or more participant IDs not found: {missing_ids}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if len(participants) < 2:
                return Response(
                    {"detail": "A conversation must have at least two participants."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"detail": "Invalid UUID format in participant_ids."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the conversation
        with transaction.atomic():
            conversation = Conversation.objects.create()
            conversation.participants.set(participants) # Set many-to-many relationship
            conversation.save()

            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def messages(self, request, pk=None):
        """
        Custom action to list or send messages within a specific conversation.
        GET: Lists all messages in the conversation.
        POST: Sends a new message to the conversation.
        """
        conversation = get_object_or_404(Conversation, conversation_id=pk)

        # Check if the requesting user is a participant in the conversation
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'GET':
            messages = conversation.messages.all().order_by('sent_at')
            serializer = MessageSerializer(messages, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = MessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Set the sender to the authenticated user and the conversation
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed or edited.
    Supports listing and retrieving messages.
    Creation of messages is primarily handled via the ConversationViewSet's 'messages' action.
    """
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend] # Add filter backend
    filterset_class = MessageFilter # Specify the filterset class

    def get_queryset(self):
        """
        Restricts messages to those sent by or received by the current user,
        or messages within conversations the user is part of.
        """
        user = self.request.user
        if user.is_authenticated:
            # Get conversations the user is part of
            user_conversations = user.conversations.all()
            # Filter messages that belong to these conversations
            return self.queryset.filter(conversation__in=user_conversations).distinct()
        return self.queryset.none()

    def perform_create(self, serializer):
        """
        Override perform_create to automatically set the sender to the authenticated user.
        This method is called when a POST request is made to the MessageViewSet directly.
        However, for messaging, it's often better to create messages via a conversation endpoint.
        """
        serializer.save(sender=self.request.user)