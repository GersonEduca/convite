import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Guest


@ensure_csrf_cookie
def invitation(request):
    return render(request, 'casamento.html')


@require_GET
def guests(request):
    data = Guest.objects.values('id', 'name', 'response')
    return JsonResponse(list(data), safe=False)


@require_POST
def respond(request, guest_id):
    try:
        payload = json.loads(request.body)
        response = payload['response']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'Resposta invalida.'}, status=400)

    valid_responses = {Guest.Response.CONFIRMED, Guest.Response.DECLINED}
    if response not in valid_responses:
        return JsonResponse({'error': 'Resposta invalida.'}, status=400)

    try:
        guest = Guest.objects.get(pk=guest_id)
    except Guest.DoesNotExist:
        return JsonResponse({'error': 'Convidado nao encontrado.'}, status=404)

    guest.response = response
    guest.save(update_fields=['response'])
    return JsonResponse({'id': guest.id, 'response': guest.response})