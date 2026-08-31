from django.contrib import admin
from django.urls import path

from guests import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/families/<slug:family_slug>/', views.family_guests, name='family_guests'),
    path('api/guests/', views.guests, name='guests'),
    path('api/guests/<int:guest_id>/respond/', views.respond, name='respond'),
    path('<slug:family_slug>/', views.invitation, name='family_invitation'),
    path('', views.invitation, name='invitation'),
]