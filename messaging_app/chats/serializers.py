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
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Includes sender details and message content.
    """
    # Nested read-only sender representation using UserSerializer
    sender = UserSerializer(read_only=True)

    # Flat representation of the sender's username for convenience
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'conversation', 'message_body',
            'sent_at', 'sender_username'
        ]
        read_only_fields = ['message_id', 'sent_at']

    def validate_message_body(self, value):
        """
        Custom validation to ensure message_body is not empty or just whitespace.
        This introduces serializers.ValidationError.
        """
        # Ensure message body is not empty or just whitespace
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Handles nested relationships for participants and messages.
    """
    # Detailed nested representation of participants
    participants = UserSerializer(many=True, read_only=True)

    # Include related messages using MessageSerializer
    messages = MessageSerializer(many=True, read_only=True)

    # Display participant usernames as comma-separated string
    participants_display = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages', 'created_at',
            'participants_display'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_participants_display(self, obj):
        """
        Returns a comma-separated string of participant usernames for display.
        """
        # Return string of usernames separated by commas
        return ", ".join([p.username for p in obj.participants.all()])
