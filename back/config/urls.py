from django.contrib import admin
from django.urls import path

from guests import views


urlpatterns = [
    path('', views.pix_contribution, name='invitation'),
    path('admin/', admin.site.urls),
    path('api/families/<slug:family_slug>/', views.family_guests, name='family_guests'),
    path('api/guests/', views.guests, name='guests'),
    path('api/guests/<int:guest_id>/respond/', views.respond, name='respond'),
    path('pix/', views.pix_contribution, name='pix_contribution'),
    path('confirmar/<slug:family_slug>/', views.confirm, name='family_invitation'),
    path('<slug:family_slug>/', views.invitation, name='invite'),
]