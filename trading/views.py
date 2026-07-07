from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Asset, Order, Transaction, Watchlist
from .serializers import (
    AssetSerializer,
    OrderCreateSerializer,
    TransactionSerializer,
    WatchlistSerializer,
)
from .throttles import OrderRateThrottle


class AssetListCreateView(generics.ListCreateAPIView):
    queryset = Asset.objects.filter(is_active=True)
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["asset_type"]
    search_fields = ["symbol", "name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class BuyOrderView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OrderRateThrottle]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["order_type"] = Order.OrderType.BUY
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        return Response(TransactionSerializer(txn).data, status=201)


class SellOrderView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OrderRateThrottle]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["order_type"] = Order.OrderType.SELL
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        txn = serializer.save()
        return Response(TransactionSerializer(txn).data, status=201)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by(
            "-executed_at"
        )


class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssetDetailView(generics.RetrieveUpdateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAdminUser]
