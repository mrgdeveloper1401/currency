from django.db import models
from django.contrib.auth.models import AbstractUser

from account_app.enums import VerifyEnum
from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class User(AbstractUser, CreateMixin, UpdateMixin, SoftDeleteMixin):
    phone = models.CharField(max_length=15, unique=True)
    verify_level = models.CharField(choices=VerifyEnum.choices, max_length=1, default=VerifyEnum.one)
    user_image = models.ForeignKey("catalog_app.Image", on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ("email", "username")

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'auth_user'


class ContentDevice(CreateMixin, UpdateMixin, SoftDeleteMixin):
    device_model = models.CharField(max_length=255, blank=True)
    device_os = models.CharField(max_length=50, blank=True)
    device_number = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_device',)
    is_blocked = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f'{self.device_model} {self.device_os} {self.ip_address}'


    class Meta:
        db_table = 'content_device'


class PrivateNotification(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255,)
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'user_private_notification'


class PublicNotification(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'public_notification'


class UserLoginLog(CreateMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_login_log")
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'user_login_log'


class Wallet(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_wallets')
    currency = models.ForeignKey("market_app.Currency", on_delete=models.PROTECT, related_name='currency_wallets')
    balance = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    class Meta:
        unique_together = ('user', 'currency')