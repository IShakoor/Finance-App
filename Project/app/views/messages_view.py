from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from app.models import Message

# render the messages page
@login_required
def messages_view(request):
    return render(request, "app/messages.html")

# get messages
@login_required
@require_GET
def get_messages(request):
    messages = Message.objects.filter(user=request.user).order_by('-created_at')
    messages.update(is_read=True)
    messages_data = [
        {
            'id': message.id,
            'title': message.title,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for message in messages
    ]
    return JsonResponse({'messages': messages_data})

# delete message
@csrf_protect
@require_POST
@login_required
def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id, user=request.user)
        message.delete()
        return JsonResponse({'success': True})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Bank account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# count unread messages
@login_required
@require_GET
def count_unread_messages(request):
    unread_messages = Message.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_messages': unread_messages})
