from django.urls import path
from .views import (
    AssetListCreateView, 
    AssetDetailView, 
    BuyOrderView, 
    SellOrderView,
    TransactionListView, 
    WatchlistListCreateView,
)

urlpatterns = [
    path("assets/", AssetListCreateView.as_view(), name="assets"),
    path("assets/<uuid:pk>/", AssetDetailView.as_view(), name="asset-detail"),
    path("orders/buy/", BuyOrderView.as_view(), name="order-buy"),
    path("orders/sell/", SellOrderView.as_view(), name="order-sell"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("watchlist/", WatchlistListCreateView.as_view(), name="watchlist"),
]