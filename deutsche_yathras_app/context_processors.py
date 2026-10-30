from .models import TourPackage


def booking_packages(request):
    return {
        "booking_packages": TourPackage.objects.order_by("-created_at")
    }