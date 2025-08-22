from django.db import models


class CurrencyEnum(models.TextChoices):
    SUM = "SO'M", "so'm"
    DOLLAR = "DOLLAR", "dollar"
    RUBLI = "RUBLI", "rubli"
