from django.contrib import admin
from .models import Asset, Order, Transaction, Watchlist

admin.site.register(Asset)
admin.site.register(Order)
admin.site.register(Transaction)
admin.site.register(Watchlist)
