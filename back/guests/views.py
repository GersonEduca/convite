import json
import secrets
from pathlib import Path

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Guest, WeddingPhoto

MAX_PHOTO_SIZE = 10 * 1024 * 1024
ALLOWED_PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def is_supported_image(image):
    header = image.read(12)
    image.seek(0)
    return (
        header.startswith(b'\xff\xd8\xff')
        or header.startswith(b'\x89PNG\r\n\x1a\n')
        or header.startswith((b'GIF87a', b'GIF89a'))
        or (header.startswith(b'RIFF') and header[8:12] == b'WEBP')
    )

def invitation(request, family_slug=None):
    context = {'family_slug': family_slug}
    if family_slug:
        context['invite'] = get_object_or_404(Guest, slug=family_slug)
    return render(request, 'convite-gerson-carine.html', context)

@ensure_csrf_cookie
def confirm(request, family_slug=None):
    context = {'family_slug': family_slug}
    if family_slug:
        context['family'] = get_object_or_404(Guest, slug=family_slug)
    return render(request, 'casamento.html', context)


@ensure_csrf_cookie
def pix_contribution(request, family_slug=None):
    context = {'family_slug': family_slug}
    if family_slug:
        get_object_or_404(Guest, slug=family_slug)
    return render(request, 'pix.html', context)


def guest_manual(request, family_slug=None):
    context = {'family_slug': family_slug}
    if family_slug:
        get_object_or_404(Guest, slug=family_slug)
    return render(request, 'manual-convidados.html', context)


@ensure_csrf_cookie
def wedding_photos(request):
    return render(request, 'fotos.html')


@require_GET
def wedding_photo_list(request):
    photos = WeddingPhoto.objects.all()
    return JsonResponse([
        {'id': photo.id, 'url': request.build_absolute_uri(photo.image.url)}
        for photo in photos
    ], safe=False)


@require_POST
def wedding_photo_upload(request):
    image = request.FILES.get('image')
    if image is None:
        return JsonResponse({'error': 'Selecione uma imagem.'}, status=400)
    if Path(image.name).suffix.lower() not in ALLOWED_PHOTO_EXTENSIONS:
        return JsonResponse({'error': 'Formato de imagem nao permitido.'}, status=400)
    if not is_supported_image(image):
        return JsonResponse({'error': 'O arquivo enviado nao e uma imagem valida.'}, status=400)
    if image.size > MAX_PHOTO_SIZE:
        return JsonResponse({'error': 'A imagem deve ter no maximo 10 MB.'}, status=400)

    photo = WeddingPhoto.objects.create(image=image)
    return JsonResponse({
        'id': photo.id,
        'url': request.build_absolute_uri(photo.image.url),
        'delete_token': str(photo.delete_token),
    }, status=201)


@require_POST
def wedding_photo_delete(request, photo_id):
    try:
        payload = json.loads(request.body)
        delete_token = payload['delete_token']
    except (KeyError, json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Nao foi possivel excluir esta imagem.'}, status=400)

    photo = get_object_or_404(WeddingPhoto, pk=photo_id)
    if not secrets.compare_digest(str(photo.delete_token), str(delete_token)):
        return JsonResponse({'error': 'Nao foi possivel excluir esta imagem.'}, status=403)

    photo.delete()
    return JsonResponse({'deleted': True})


@require_GET
def guests(request):
    guests = Guest.objects.all().order_by('name')
    data = []
    for guest in guests:
        item = {
            'id': guest.id,
            'name': guest.display_name,
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
            'name': guest.display_name,
            'first_name': guest.first_name,
            'response': guest.response,
            'family_head_id': guest.family_head_id,
            'slug': guest.slug,
        })
    return JsonResponse({
        'head': {'id': family_head.id, 'name': family_head.display_name, 'first_name': family_head.first_name},
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