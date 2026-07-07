from rest_framework.throttling import UserRateThrottle


class OrderRateThrottle(UserRateThrottle):
    scope = "orders"
