from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, default='manager')

    def __str__(self):
        return f'{self.user.username} ({self.role})'


class Car(models.Model):
    STATUS_CHOICES = [
        ('in_stock', 'На складе'),
        ('sold', 'Продан'),
    ]

    vin        = models.CharField(max_length=17, unique=True)
    model      = models.CharField(max_length=50)
    year       = models.PositiveIntegerField(null=True, blank=True)
    color      = models.CharField(max_length=30, blank=True)
    price      = models.DecimalField(max_digits=12, decimal_places=2)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in_stock')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.model} ({self.vin})'


class Log(models.Model):
    ACTION_CHOICES = [
        ('accept', 'Приёмка'),
        ('sale', 'Продажа'),
    ]

    car      = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='logs')
    action   = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user     = models.ForeignKey(User, on_delete=models.PROTECT, related_name='logs')
    log_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-log_date']
        indexes = [
            models.Index(fields=['action', 'log_date']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.get_action_display()} — {self.car} — {self.user.username}'