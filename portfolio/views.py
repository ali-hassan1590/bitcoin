from rest_framework import generics, permissions
from .models import Portfolio
from .serializers import PortfolioSerializer


class PortfolioListView(generics.ListAPIView):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user, quantity__gt=0)
