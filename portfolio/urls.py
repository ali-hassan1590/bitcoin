from django.urls import path
from .views import PortfolioListView

urlpatterns = [
    path("portfolio/", PortfolioListView.as_view(), name="portfolio"),
]