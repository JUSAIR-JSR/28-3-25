
from django.utils import timezone

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Conversation, Message

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Conversation, Message

@login_required
def chat_home(request):
    user = request.user
    query = request.GET.get('query', '')

    if query:
        users = User.objects.filter(username__icontains=query).exclude(username=request.user.username)
    else:
        users = User.objects.none()

    # Handle POST request to delete a conversation
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        Conversation.objects.filter(id=conversation_id).delete()
        return redirect('chat_home')

    conversations = (Conversation.objects.filter(Q(participant1=user) | Q(participant2=user))).distinct()
    
    # Remove duplicate participants and check for unread messages
    seen_users = set()
    filtered_conversations = []
    for conversation in conversations:
        other_participant = conversation.participant1 if conversation.participant2 == request.user else conversation.participant2
        if other_participant.username not in seen_users:
            seen_users.add(other_participant.username)
            has_unread_messages = conversation.messages.filter(is_read=False).exists()
            filtered_conversations.append({
                'conversation': conversation,
                'other_participant': other_participant,
                'has_unread_messages': has_unread_messages,
            })
            other_participant.profile_image_url = other_participant.profile.profile_image.url if hasattr(other_participant, 'profile') and other_participant.profile.profile_image else None

    return render(request, 'chat/home.html', {
        'conversations': filtered_conversations, 
        'users': users, 
        'query': query
    })




@login_required
def chat_room(request, username):
    participant1 = request.user
    participant2 = get_object_or_404(User, username=username)

    # Retrieve or create the conversation
    conversation = Conversation.objects.filter(
        Q(participant1=participant1, participant2=participant2) | 
        Q(participant1=participant2, participant2=participant1)
    ).first()
    
    if not conversation:
        conversation = Conversation.objects.create(participant1=participant1, participant2=participant2)

    # Handle POST requests to send, edit, or delete messages
    if request.method == 'POST':
        action = request.POST.get('action')
        message_text = request.POST.get('message')
        message_id = request.POST.get('message_id')

        if action == 'send':
            Message.objects.create(conversation=conversation, sender=request.user, text=message_text, timestamp=timezone.now())
        elif action == 'edit':
            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.text = message_text
            message.save()
        elif action == 'delete':
            message = get_object_or_404(Message, id=message_id, sender=request.user)
            message.delete()

        return redirect('chat_room', username=username)

    # Mark messages as read
    conversation.messages.filter(sender=participant2, is_read=False).update(is_read=True)

    # Retrieve all messages for the conversation
    messages = conversation.messages.all().order_by('timestamp')

    return render(request, 'chat/chat_room.html', {'conversation': conversation, 'messages': messages, 'other_participant': participant2})


