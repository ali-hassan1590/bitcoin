from decimal import Decimal
from django.db import transaction as db_transaction
from rest_framework import serializers

from .models import Asset, Order, Transaction, Watchlist
from portfolio.models import Portfolio
from wallet.models import Wallet
from notifications.tasks import send_order_notification


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "symbol",
            "name",
            "asset_type",
            "current_price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OrderCreateSerializer(serializers.Serializer):
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())
    quantity = serializers.DecimalField(max_digits=15, decimal_places=4)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate_asset(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This asset is not active/tradable.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        order_type = self.context["order_type"]  # "buy" or "sell"
        asset = attrs["asset"]
        quantity = attrs["quantity"]
        price = asset.current_price
        total_cost = price * quantity

        if order_type == Order.OrderType.BUY:
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance < total_cost:
                raise serializers.ValidationError(
                    {"quantity": "Insufficient wallet balance for this order."}
                )
        else:  # sell
            holding = Portfolio.objects.filter(user=request.user, asset=asset).first()
            if not holding or holding.quantity < quantity:
                raise serializers.ValidationError(
                    {"quantity": "You do not hold enough of this asset to sell."}
                )

        attrs["price"] = price
        attrs["total_cost"] = total_cost
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        order_type = self.context["order_type"]
        asset = validated_data["asset"]
        quantity = validated_data["quantity"]
        price = validated_data["price"]
        total_cost = validated_data["total_cost"]

        with db_transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                asset=asset,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status=Order.Status.PENDING,
            )

            wallet = Wallet.objects.select_for_update().get(user=request.user)
            holding, _ = Portfolio.objects.select_for_update().get_or_create(
                user=request.user,
                asset=asset,
                defaults={"quantity": 0, "average_buy_price": 0},
            )

            if order_type == Order.OrderType.BUY:
                wallet.balance -= total_cost
                new_quantity = holding.quantity + quantity
                # weighted average buy price
                holding.average_buy_price = (
                    (holding.quantity * holding.average_buy_price) + (quantity * price)
                ) / new_quantity
                holding.quantity = new_quantity
            else:  # sell
                wallet.balance += total_cost
                holding.quantity -= quantity
                # average_buy_price stays the same on a sell

            wallet.save()
            holding.save()

            order.status = Order.Status.EXECUTED
            order.save()

            txn = Transaction.objects.create(
                user=request.user,
                order=order,
                asset=asset,
                order_type=order_type,
                quantity=quantity,
                price=price,
                total_amount=total_cost,
            )

        # Fires only after the transaction block commits successfully.
        # .delay() hands this off to Redis/Celery immediately — the API
        # response does not wait for the notification to be created.
        send_order_notification.delay(
            request.user.id,
            f"{order_type.upper()} order executed: {quantity} {asset.symbol} @ {price}",
        )

        return txn


class TransactionSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "asset_symbol",
            "order_type",
            "quantity",
            "price",
            "total_amount",
            "executed_at",
        ]


class WatchlistSerializer(serializers.ModelSerializer):
    asset_detail = AssetSerializer(source="asset", read_only=True)

    class Meta:
        model = Watchlist
        fields = ["id", "asset", "asset_detail", "added_at"]
        read_only_fields = ["id", "added_at"]

    def validate_asset(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Cannot watch an inactive asset.")
        return value
