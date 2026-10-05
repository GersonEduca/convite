from django.contrib import admin
from django.urls import path

from guests import views


urlpatterns = [
    path('', views.guest_manual, name='invitation'),
    path('ademiro/', admin.site.urls),
    path('api/families/<slug:family_slug>/', views.family_guests, name='family_guests'),
    path('api/guests/', views.guests, name='guests'),
    path('api/guests/<int:guest_id>/respond/', views.respond, name='respond'),
    path('pix/<slug:family_slug>/', views.pix_contribution, name='family_pix'),
    path('pix/', views.pix_contribution, name='pix_contribution'),
    path('manual/<slug:family_slug>/', views.guest_manual, name='family_manual'),
    path('manual/', views.guest_manual, name='manual_convidados'),
    path('confirmar/<slug:family_slug>/', views.confirm, name='family_invitation'),
    path('<slug:family_slug>/', views.invitation, name='invite'),
]