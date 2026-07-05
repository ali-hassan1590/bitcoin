import random
from decimal import Decimal
from celery import shared_task
from .models import Asset


@shared_task
def simulate_price_changes():
    """
    Runs automatically every 30s via Celery Beat.
    In a real app this would call an external market-data API instead.
    """
    for asset in Asset.objects.filter(is_active=True):
        change_percent = Decimal(random.uniform(-2, 2)) / 100  # -2% to +2%
        new_price = asset.current_price * (1 + change_percent)
        asset.current_price = round(new_price, 2)
        asset.save(update_fields=["current_price"])