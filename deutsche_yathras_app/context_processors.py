from .models import Destination, TourPackage


def booking_packages(request):
    packages = TourPackage.objects.order_by("-created_at")
    return {
        "booking_packages": packages,                       # booking modal (unchanged)
        "nav_packages": packages[:10],                      # Packages dropdown
        "nav_destinations": Destination.objects.order_by("-created_at")[:10],   # Destinations dropdown
    }