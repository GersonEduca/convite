# -*- coding: utf-8 -*-

import re
from urllib.parse import quote

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from openpyxl import load_workbook

from .models import Guest


class GuestImportForm(forms.Form):
    file = forms.FileField(label='Arquivo Excel (.xlsx)')


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'family_head', 'phone', 'response', 'whatsapp_link')
    list_filter = ('response', 'family_head')
    search_fields = ('name', 'phone', 'notes')
    change_list_template = 'admin/guests/guest/change_list.html'

    @staticmethod
    def normalize_phone(phone):
        digits = re.sub(r'\D', '', str(phone or ''))
        if not digits:
            return ''

        if digits.startswith('55') and len(digits) == 13:
            return digits
        if digits.startswith('55') and len(digits) == 12:
            return digits
        if len(digits) == 11:
            return f'55{digits}'
        if len(digits) == 10:
            return f'55{digits}'
        return digits

    def build_whatsapp_message(self, obj):
        family = obj.family_head or obj
        family_slug = family.slug if getattr(family, 'slug', None) else ''
        base_url = settings.APP_BASE_URL.rstrip('/')

        invite_url = f'{base_url}/{family_slug}' if family_slug else base_url
        #image_url = f'{base_url}{settings.STATIC_URL}bg-top.png'

        return (
            '✨💍 Carine & Gerson 💍✨\n'
            'Você faz parte da nossa história e não poderia ficar de fora desse dia tão especial! 👰‍♀️🤵‍♂️✨\n\n'
            'Venha celebrar o nosso casamento conosco, a sua presença é fundamental para tornar esse dia ainda mais especial! 🥂\n\n'
            'Confirme sua presença pelo link:\n'
            f'{invite_url}\n\n'
        )

    def whatsapp_link(self, obj):
        phone = self.normalize_phone(obj.phone)
        if not phone:
            return '-' 

        message = quote(self.build_whatsapp_message(obj))
        url = f'https://wa.me/{phone}?text={message}'
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" style="display:inline-block;padding:6px 12px;border-radius:6px;background:#25D366;color:#fff;text-decoration:none;font-weight:600;">WhatsApp</a>',
            url,
        )

    whatsapp_link.short_description = 'WhatsApp'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-xlsx/', self.admin_site.admin_view(self.import_xlsx_view), name='guests_guest_import_xlsx'),
        ]
        return custom_urls + urls

    def import_xlsx_view(self, request):
        if request.method == 'POST':
            form = GuestImportForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file']
                workbook = load_workbook(uploaded_file, read_only=True, data_only=True)
                sheet = workbook.active
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    messages.error(request, 'O arquivo enviado está vazio.')
                    return HttpResponseRedirect(reverse('admin:guests_guest_changelist'))

                columns = [str(value).strip() if value is not None else '' for value in rows[0]]
                if not columns:
                    messages.error(request, 'Não foi possível identificar as colunas do arquivo.')
                    return HttpResponseRedirect(reverse('admin:guests_guest_changelist'))

                def header_index(name):
                    for idx, column in enumerate(columns):
                        if column.lower() == name.lower():
                            return idx
                    return -1

                index_id = header_index('ID')
                index_name = header_index('Convidados')
                index_chefe_id = header_index('Chefe_Id')
                index_telefone = header_index('Telefone')
                index_obs = header_index('Observação')

                if index_name == -1:
                    messages.error(request, 'A coluna "Convidados" é obrigatória no arquivo XLSX.')
                    return HttpResponseRedirect(reverse('admin:guests_guest_changelist'))

                def normalize_name(value):
                    if value is None:
                        return ''
                    return ' '.join(str(value).strip().split())

                def normalize_sheet_id(value):
                    if value is None:
                        return ''
                    text = normalize_name(value)
                    if not text or text.lower() == 'none':
                        return ''
                    try:
                        numeric = float(text)
                    except ValueError:
                        return text
                    if numeric.is_integer():
                        return str(int(numeric))
                    return text

                def row_value(row, index):
                    if index < 0 or index >= len(row):
                        return ''
                    value = row[index]
                    return '' if value is None else normalize_name(value)

                def find_or_create_guest(name, source_id=''):
                    normalized = normalize_name(name)

                    if source_id:
                        try:
                            source_pk = int(source_id)
                        except (ValueError, TypeError):
                            source_pk = None

                        if source_pk is not None:
                            guest = Guest.objects.filter(pk=source_pk).first()
                            if guest is not None:
                                if guest.name != normalized:
                                    guest.name = normalized
                                    guest.save(update_fields=['name'])
                                return guest
                            return Guest.objects.create(id=source_pk, name=normalized)

                    return Guest.objects.create(name=normalized)

                def fix_duplicate_head_slugs():
                    for guest in Guest.objects.filter(family_head__isnull=True).order_by('id'):
                        if not guest.slug:
                            guest.slug = guest.generate_unique_slug()
                            guest.save(update_fields=['slug'])

                fix_duplicate_head_slugs()

                created_map = {}
                created_by_id = {}

                for row in rows[1:]:
                    if not row:
                        continue

                    name = row_value(row, index_name)
                    if not name:
                        continue

                    source_id = normalize_sheet_id(row_value(row, index_id))
                    key = (source_id or name).lower()
                    if key not in created_map:
                        created_map[key] = find_or_create_guest(name, source_id)
                    if source_id:
                        created_by_id[source_id.lower()] = created_map[key]

                    guest = created_map[key]
                    guest.phone = row_value(row, index_telefone)
                    guest.notes = row_value(row, index_obs)
                    guest.family_head = None
                    if not guest.slug:
                        guest.slug = guest.generate_unique_slug(source_id=source_id)
                    guest.save()

                with transaction.atomic():
                    for row in rows[1:]:
                        if not row:
                            continue

                        name = row_value(row, index_name)
                        if not name:
                            continue

                        source_id = normalize_sheet_id(row_value(row, index_id))
                        chefe_id = normalize_sheet_id(row_value(row, index_chefe_id))
                        guest_key = (source_id or name).lower()
                        guest = created_map.get(guest_key)
                        if guest is None:
                            continue

                        family_head = None
                        if chefe_id:
                            family_head = created_by_id.get(chefe_id.lower())
                            if family_head is None:
                                try:
                                    family_head = Guest.objects.filter(pk=int(chefe_id)).first()
                                except (ValueError, TypeError):
                                    family_head = None

                        guest.family_head = family_head

                        if source_id and guest.slug in (None, ''):
                            guest.slug = guest.generate_unique_slug(source_id=source_id)
                        elif not guest.slug:
                            guest.slug = guest.generate_unique_slug()
                        guest.save()

                messages.success(request, f'Arquivo importado com sucesso. {len(created_map)} convidados foram processados.')
                return HttpResponseRedirect(reverse('admin:guests_guest_changelist'))

        form = GuestImportForm()
        context = {
            'opts': self.model._meta,
            'form': form,
            'title': 'Importar convidados via XLSX',
        }
        return render(request, 'admin/guests/guest/import_xlsx.html', context)