from django.db import models
from django.utils.text import slugify


class Guest(models.Model):
    class Response(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        DECLINED = 'declined', 'Negado'

    name = models.CharField('Nome', max_length=120)
    family_head = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='family_members',
        null=True,
        blank=True,
        verbose_name='Chefe da família',
    )
    phone = models.CharField('Telefone', max_length=30, blank=True, default='')
    notes = models.TextField('Observação', blank=True, default='')
    response = models.CharField(
        'Resposta',
        max_length=20,
        choices=Response.choices,
        default=Response.PENDING,
    )
    slug = models.SlugField('Slug da família', max_length=120, unique=True, blank=True, null=True)

    @property
    def first_name(self):
        if not self.name:
            return ''
        return self.name.strip().split()[0]

    def generate_unique_slug(self, source_id=None):
        base_slug = slugify(self.name) or 'convidado'
        candidate = base_slug

        if source_id:
            source_token = slugify(str(source_id))
            if source_token:
                candidate = f'{base_slug}-{source_token}'
                if not Guest.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                    return candidate

        counter = 2
        while Guest.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f'{base_slug}-{counter}'
            counter += 1
        return candidate

    def save(self, *args, **kwargs):
        if self.family_head_id is not None:
            self.slug = None
        else:
            if not self.slug:
                self.slug = self.generate_unique_slug()
            elif Guest.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)

    @property
    def family_name(self):
        return self.family_head.name if self.family_head else self.name

    def __str__(self):
        return self.name