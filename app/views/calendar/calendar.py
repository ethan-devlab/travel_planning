from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ...models import Event
import json
import datetime

@login_required
def calendar_view(request):
    return render(request, 'calendar/calendar.html')


def get_events(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    events = Event.objects.filter(owner=request.user)
    data = []
    for event in events:
        data.append({
            'id': event.id,  # Include event ID
            'eventName': event.event_name,
            'date': event.date.strftime('%Y-%m-%d'),
            'color': event.color,
            'calendar': event.color
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def add_event(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('eventName')
            date = datetime.datetime.strptime(data.get('date'), '%Y-%m-%d').date()
            color = data.get('color')
            
            event = Event.objects.create(owner=request.user, event_name=name, date=date, color=color)
            return JsonResponse({
                'status': 'ok', 
                'id': event.id,
                'eventName': name
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
