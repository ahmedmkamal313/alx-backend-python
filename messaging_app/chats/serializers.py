from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    Includes essential user fields.
    """
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'role', 'created_at'
        ]
        # These are set automatically
        read_only_fields = ['user_id', 'created_at']
        # Optionally, exclude password_hash if you don't want it exposed
        # extra_kwargs = {'password': {'write_only': True}} # If you were handling password creation/update here


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes sender details and message content.
    """
    # Use a nested serializer for the sender to show more than just the ID
    # Use UserSerializer for a detailed representation of the sender
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'conversation', 'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
        # The 'conversation' field is a ForeignKey, so it will typically
        # be represented by its PK (UUID) when writing/reading.


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles nested relationships for participants and messages.
    """
    # Nested serializer for participants (many-to-many relationship)
    # Use UserSerializer to represent each participant in detail
    participants = UserSerializer(many=True, read_only=True)

    # Nested serializer for messages within the conversation (reverse foreign key)
    # Use MessageSerializer to represent each message
    # 'messages' is the related_name defined in the Message model's ForeignKey to Conversation
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
