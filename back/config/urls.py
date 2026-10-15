from django.contrib import admin
from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from guests import views


urlpatterns = [
    path('', views.guest_manual, name='invitation'),
    path('ademiro/', admin.site.urls),
    path('api/families/<slug:family_slug>/', views.family_guests, name='family_guests'),
    path('api/guests/', views.guests, name='guests'),
    path('api/guests/<int:guest_id>/respond/', views.respond, name='respond'),
    path('pix/<slug:family_slug>/', views.pix_contribution, name='family_pix'),
    path('pix/', views.pix_contribution, name='pix_contribution'),
    path('fotos/', views.wedding_photos, name='wedding_photos'),
    path('api/fotos/', views.wedding_photo_list, name='wedding_photo_list'),
    path('api/fotos/upload/', views.wedding_photo_upload, name='wedding_photo_upload'),
    path('api/fotos/<int:photo_id>/excluir/', views.wedding_photo_delete, name='wedding_photo_delete'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('manual/<slug:family_slug>/', views.guest_manual, name='family_manual'),
    path('manual/', views.guest_manual, name='manual_convidados'),
    path('confirmar/<slug:family_slug>/', views.confirm, name='family_invitation'),
    path('<slug:family_slug>/', views.invitation, name='invite'),
]