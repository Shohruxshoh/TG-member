from django.db import models


class Currency(models.TextChoices):
    SUM = "SO'M", "so'm"
    DOLLAR = "DOLLAR", "dollar"
    RUBLI = "RUBLI", "rubli"
