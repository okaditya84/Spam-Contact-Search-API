from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, name, password=None, email=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, name=name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, name, password, email, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'{self.name} ({self.phone_number})'

class Contact(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.name} ({self.phone_number})'

class SpamReport(models.Model):
    phone_number = models.CharField(max_length=15)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='spam_reports')
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('phone_number', 'reported_by')

    def __str__(self):
        return f'Spam report for {self.phone_number} by {self.reported_by.phone_number}'
