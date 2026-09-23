import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Guest


@ensure_csrf_cookie
def invitation(request, family_slug=None):
    context = {'family_slug': family_slug}
    if family_slug:
        context['family'] = get_object_or_404(Guest, slug=family_slug)
    return render(request, 'casamento.html', context)


@require_GET
def guests(request):
    guests = Guest.objects.all().order_by('name')
    data = []
    for guest in guests:
        item = {
            'id': guest.id,
            'name': guest.name,
            'first_name': guest.first_name,
            'response': guest.response,
            'family_head_id': guest.family_head_id,
            'slug': guest.slug,
        }
        data.append(item)
    return JsonResponse(data, safe=False)


@require_GET
def family_guests(request, family_slug):
    family_head = get_object_or_404(Guest, slug=family_slug)
    members = Guest.objects.filter(Q(pk=family_head.pk) | Q(family_head=family_head)).order_by('name')
    payload_members = []
    for guest in members:
        payload_members.append({
            'id': guest.id,
            'name': guest.name,
            'first_name': guest.first_name,
            'response': guest.response,
            'family_head_id': guest.family_head_id,
            'slug': guest.slug,
        })
    return JsonResponse({
        'head': {'id': family_head.id, 'name': family_head.name, 'first_name': family_head.first_name},
        'members': payload_members,
    })


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