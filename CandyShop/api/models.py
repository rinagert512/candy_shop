from django.db import models
from .validators import validate_hours, validate_regions
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField


class Courier(models.Model):
    REQUIRED_FIELDS = [
        'courier_id',
        'courier_type',
        'regions',
        'working_hours'
    ]

    TYPE_CHOICES = [
        ("foot", "foot"),
        ("bike", "bike"),
        ("car", "car")
    ]

    courier_id = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(0)]
    )
    courier_type = models.CharField(
        verbose_name="Тип курьера",
        choices=TYPE_CHOICES,
        max_length=4
    )
    regions = ArrayField(
        verbose_name="Регионы",
        base_field=models.IntegerField(),
        validators=[validate_regions]
    )
    working_hours = ArrayField(
        verbose_name="График работы курьера",
        base_field=models.CharField(
            max_length=11
        ),
        validators=[validate_hours],
        blank=True
    )

    def __str__(self):
        return "Курьер №" + str(self.courier_id)

    class Meta:
        verbose_name = "Курьер"
        verbose_name_plural = "Курьеры"


class Order(models.Model):
    REQUIRED_FIELDS = [
        "order_id",
        "weight",
        "region",
        "delivery_hours"
    ]

    order_id = models.AutoField(primary_key=True)
    weight = models.FloatField(
        verbose_name="Вес заказа",
        validators=[
            MinValueValidator(0.01),
            MaxValueValidator(50)
        ]
    )
    region = models.IntegerField(
        verbose_name="Район доставки заказа",
        validators=[MinValueValidator(0)]
    )
    delivery_hours = ArrayField(
        verbose_name="Удобное время доставки",
        base_field=models.CharField(
            max_length=11
        ),
        validators=[validate_hours]
    )
    courier = models.ForeignKey(
        Courier,
        blank=True,
        null=True,
        verbose_name="Курьер, доставляющий заказ",
        on_delete=models.CASCADE
    )
    assign_time = models.DateTimeField(
        "Время назначения заказа",
        default=None,
        blank=True,
        null=True
    )
    complete_time = models.DateTimeField(
        "Время окончания доставки заказа",
        default=None,
        blank=True,
        null=True
    )

    def __str__(self):
        return "Заказ №" + str(self.order_id)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
