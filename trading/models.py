import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Asset(models.Model):
    class AssetType(models.TextChoices):
        STOCK = "stock", "Stock"
        CRYPTO = "crypto", "Crypto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=10, choices=AssetType.choices)
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Order(models.Model):
    class OrderType(models.TextChoices):
        BUY = "buy", "Buy"
        SELL = "sell", "Sell"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        EXECUTED = "executed", "Executed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="orders")
    order_type = models.CharField(max_length=4, choices=OrderType.choices)
    quantity = models.DecimalField(
        max_digits=15, decimal_places=4, validators=[MinValueValidator(0.0001)]
    )
    price = models.DecimalField(
        max_digits=15, decimal_places=2
    )  # price at time of order
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_type.upper()} {self.quantity} {self.asset.symbol} @ {self.price}"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    order = models.OneToOneField(
        Order, on_delete=models.PROTECT, related_name="transaction"
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name="transactions"
    )
    order_type = models.CharField(max_length=4, choices=Order.OrderType.choices)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_type.upper()} {self.quantity} {self.asset.symbol} @ {self.price}"


class Watchlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist"
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="watched_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "asset")

    def __str__(self):
        return f"{self.user.email} watching {self.asset.symbol}"
