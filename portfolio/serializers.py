from rest_framework import serializers
from .models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="asset.symbol", read_only=True)
    name = serializers.CharField(source="asset.name", read_only=True)
    current_price = serializers.DecimalField(source="asset.current_price", max_digits=15, decimal_places=2, read_only=True)
    current_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            "id", "symbol", "name", "quantity", "average_buy_price",
            "current_price", "current_value", "profit_loss", "updated_at",
        ]

    def get_current_value(self, obj):
        return round(obj.quantity * obj.asset.current_price, 2)

    def get_profit_loss(self, obj):
        return round((obj.asset.current_price - obj.average_buy_price) * obj.quantity, 2)