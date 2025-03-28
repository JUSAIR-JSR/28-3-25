from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participant1 = models.ForeignKey(User, related_name='conversations_as_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='conversations_as_participant2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # New field to track if the message has been read