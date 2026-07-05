import uuid
from django.conf import settings
from django.db import models
from trading.models import Asset


class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolio_holdings"
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="held_by")
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    average_buy_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "asset")

    def __str__(self):
        return f"{self.user.email} - {self.asset.symbol}: {self.quantity}"