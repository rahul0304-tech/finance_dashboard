from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('VIEWER', 'Viewer'),
        ('ANALYST', 'Analyst'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='VIEWER')

class FinancialRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class FinancialRecord(models.Model):
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = FinancialRecordManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
        
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.date}"
