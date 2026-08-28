from django.db import models


class Guest(models.Model):
    class Response(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        DECLINED = 'declined', 'Negado'

    name = models.CharField(max_length=120)
    response = models.CharField(
        max_length=20,
        choices=Response.choices,
        default=Response.PENDING,
    )

    def __str__(self):
        return self.name