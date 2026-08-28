from django.contrib import admin

from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'response')
    list_filter = ('response',)
    search_fields = ('name',)