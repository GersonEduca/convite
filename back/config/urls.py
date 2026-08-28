from django.contrib import admin
from django.urls import path

from guests import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.invitation, name='invitation'),
    path('api/guests/', views.guests, name='guests'),
    path('api/guests/<int:guest_id>/respond/', views.respond, name='respond'),
]