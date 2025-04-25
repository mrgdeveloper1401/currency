from django.db import models


class VerifyEnum(models.TextChoices):
    one = '1'
    two = '2'
    three = '3'
