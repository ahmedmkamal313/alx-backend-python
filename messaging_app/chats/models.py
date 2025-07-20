import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    It uses a UUID as the primary key and adds specific fields
    like phone_number and role as per the project requirements.
    """
    # Overide the default primary key to use UUID
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text="Unique identifier for the user")

    # Fields from the specification not covered by AbstractUser
    # AbstractUser already has first_name, last_name, email, password (hashed)
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="User's phone number (optional)")

    # Role field to define user roles
    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.GUEST,
        null=False,
        blank=False,
        help_text="Role of the user in the application"
    )

    # created_at field as per specification
    created_at = models.DateTimeField(default=timezone.now,
                                      help_text="Timestamp when the user account was created")

    # Set email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = 'email'
    # Remove 'email' from REQUIRED_FIELDS as it's the USERNAME_FIELD
    # These will be prompted when creating a superuser
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        """ String representation of the User model """
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['created_at']  # Order users by creation date, newest first

    def __str__(self):
        """String representation of the User."""
        return self.email


class Conversation(models.Model):
    """
    Represents a conversation between multiple users.
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                       editable=False, help_text="Unique identifier for the conversation")

    # Many-to-Many relationship with the custom User model
    # related_name='conversations' allows accessing conversations from a User instance (e.g., user.conversations.all())
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text="Users involved in this conversation"
    )

    created_at = models.DateTimeField(default=timezone.now,
                                      help_text="Timestamp when the conversation was created")

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        # Order conversations by creation date, newest first
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the Conversation."""
        # Display participants' emails for a more descriptive string
        participant_emails = ", ".join(
            [user.email for user in self.participants.all()])
        return f"Conversation {self.conversation_id} with: {participant_emails}"


class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False, help_text="Unique identifier for the message")

    # Foreign Key to the User model for the sender
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # If a user is deleted, their sent messages are also deleted
        related_name='sent_messages',  # Allows accessing sent messages from a User instance
        help_text="The user who sent this message"
    )

    # Foreign Key to the Conversation model
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,  # If a conversation is deleted, its messages are also deleted
        related_name='messages',  # Allows accessing messages from a Conversation instance
        help_text="The conversation this message belongs to"
    )

    message_body = models.TextField(
        null=False, blank=False, help_text="The content of the message")

    sent_at = models.DateTimeField(
        default=timezone.now, help_text="Timestamp when the message was sent")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        # Order messages chronologically within a conversation
        ordering = ['sent_at']

    def __str__(self):
        """String representation of the Message."""
        return f"Message from {self.sender.email} in Conversation {
            self.conversation.conversation_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
