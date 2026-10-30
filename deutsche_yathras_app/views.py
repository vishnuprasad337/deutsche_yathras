from functools import wraps
from urllib import request

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    BlogForm,
    CategoryForm,
    DestinationForm,
    TestimonialForm,
    TourPackageForm,
)

from .models import (
    Blog,
    BookingEnquiry,
    Category,
    ContactMessage,
    Destination,
    GalleryImage,
    Testimonial,
    TourPackage,
)



# ============================================================
# ADMIN ACCESS DECORATOR
# ============================================================

def admin_required(view_func):

    @wraps(view_func)
    @login_required(login_url="admin-login")
    def wrapper(request, *args, **kwargs):

        if not request.user.is_staff:
            messages.error(
                request,
                "You do not have permission to access the admin dashboard."
            )

            logout(request)

            return redirect("admin_login")

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# ADMIN LOGIN
# ============================================================

def admin_login(request):

    # Already logged in as an admin
    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        logout(request)


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )


        # Required fields
        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return render(
                request,
                "authenticate/login.html",
            )


        # Authenticate
        user = authenticate(
            request,
            username=username,
            password=password,
        )


        if user is not None and user.is_staff:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect(
                "admin_dashboard"
            )


        messages.error(
            request,
            "Invalid username, password, or unauthorized access."
        )


    return render(
        request,
        "authenticate/login.html",
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@admin_required
def admin_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "admin-login"
    )






# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_required
def admin_dashboard(request):

    now = timezone.now()

    month_start = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


    # ========================================================
    # STATISTICS
    # ========================================================

    stats = {

        "total_packages":
            TourPackage.objects.count(),

        "total_destinations":
            Destination.objects.count(),

        "total_blogs":
            Blog.objects.count(),

        "blogs_this_month":
            Blog.objects.filter(
                created_at__gte=month_start
            ).count(),

        "total_gallery":
            GalleryImage.objects.count(),

        "total_testimonials":
            Testimonial.objects.count(),

        "total_contacts":
            ContactMessage.objects.count(),

        "total_enquiries":
            BookingEnquiry.objects.count(),
    }


    # ========================================================
    # RECENT DATA
    # ========================================================

    recent_packages = (
        TourPackage.objects
        .order_by("-created_at")[:5]
    )

    recent_destinations = (
        Destination.objects
        .order_by("-created_at")[:5]
    )

    recent_blogs = (
        Blog.objects
        .order_by("-created_at")[:5]
    )

    recent_contacts = (
        ContactMessage.objects
        .order_by("-created_at")[:5]
    )

    recent_enquiries = (
        BookingEnquiry.objects
        .order_by("-created_at")[:5]
    )


    context = {

        "stats": stats,

        "recent_packages":
            recent_packages,

        "recent_destinations":
            recent_destinations,

        "recent_blogs":
            recent_blogs,

        "recent_contacts":
            recent_contacts,

        "recent_enquiries":
            recent_enquiries,
    }


    return render(
        request,
        "admin_pages/dashboard.html",
        context,
    )





# ============================================================
# BLOGS
# ============================================================

@admin_required
def admin_blog_list(request):

    blogs = Paginator(
        Blog.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/blog_list.html",
        {
            "blogs": blogs,
        },
    )


@admin_required
def blog_create(request):

    form = BlogForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Blog created successfully."
        )

        return redirect(
            "admin_blog_list"
        )

    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "form": form,
        },
    )


@admin_required
def blog_update(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    form = BlogForm(
        request.POST or None,
        request.FILES or None,
        instance=blog,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Blog updated successfully."
        )

        return redirect(
            "admin_blog_list"
        )

    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "form": form,
            "blog": blog,
        },
    )


@admin_required
def blog_delete(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    if request.method == "POST":

        blog.delete()

        messages.success(
            request,
            "Blog deleted successfully."
        )

    return redirect(
        "admin_blog_list"
    )





# ============================================================
# TOUR PACKAGES
# ============================================================

@admin_required
def admin_package_list(request):

    packages = Paginator(
        TourPackage.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/package_list.html",
        {
            "packages": packages,
        },
    )


@admin_required
def package_create(request):

    form = TourPackageForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Tour package created successfully."
        )

        return redirect(
            "admin_package_list"
        )

    return render(
        request,
        "admin_pages/create_package.html",
        {
            "form": form,
        },
    )


@admin_required
def package_update(request, pk):

    package = get_object_or_404(
        TourPackage,
        pk=pk,
    )

    form = TourPackageForm(
        request.POST or None,
        request.FILES or None,
        instance=package,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Tour package updated successfully."
        )

        return redirect(
            "admin_package_list"
        )

    return render(
        request,
        "admin_pages/create_package.html",
        {
            "form": form,
            "package": package,
        },
    )


@admin_required
def package_delete(request, pk):

    package = get_object_or_404(
        TourPackage,
        pk=pk,
    )

    if request.method == "POST":

        package.delete()

        messages.success(
            request,
            "Tour package deleted successfully."
        )

    return redirect(
        "admin_package_list"
    )




# ============================================================
# DESTINATIONS
# ============================================================

@admin_required
def admin_destination_list(request):

    destinations = Paginator(
        Destination.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/destination_list.html",
        {
            "destinations": destinations,
        },
    )


@admin_required
def destination_create(request):

    form = DestinationForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Destination created successfully."
        )

        return redirect(
            "admin_destination_list"
        )

    return render(
        request,
        "admin_pages/create_destination.html",
        {
            "form": form,
        },
    )


@admin_required
def destination_update(request, pk):

    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    form = DestinationForm(
        request.POST or None,
        request.FILES or None,
        instance=destination,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Destination updated successfully."
        )

        return redirect(
            "admin_destination_list"
        )

    return render(
        request,
        "admin_pages/create_destination.html",
        {
            "form": form,
            "destination": destination,
        },
    )


@admin_required
def destination_delete(request, pk):

    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    if request.method == "POST":

        destination.delete()

        messages.success(
            request,
            "Destination deleted successfully."
        )

    return redirect(
        "admin_destination_list"
    )





# ============================================================
# GALLERY
# ============================================================

@admin_required
def gallery_images(request):

    categories = (
        Category.objects
        .prefetch_related("images")
        .order_by("name")
    )

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
        },
    )


@admin_required
def add_image(request):

    categories = Category.objects.order_by(
        "name"
    )

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        files = request.FILES.getlist(
            "images"
        )

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories,
                },
            )


        category = get_object_or_404(
            Category,
            pk=category_id,
        )


        if not files:

            messages.error(
                request,
                "Please select at least one image."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories,
                },
            )


        for image_file in files:

            GalleryImage.objects.create(
                category=category,
                title=image_file.name,
                image=image_file,
            )


        messages.success(
            request,
            "Gallery images uploaded successfully."
        )

        return redirect(
            "list_image"
        )


    return render(
        request,
        "admin_pages/add_image.html",
        {
            "categories": categories,
        },
    )


@admin_required
def delete_image(request, image_id):

    image = get_object_or_404(
        GalleryImage,
        pk=image_id,
    )

    if request.method == "POST":

        image.delete()

        messages.success(
            request,
            "Gallery image deleted successfully."
        )

    return redirect(
        "list_image"
    )





# ============================================================
# CATEGORIES
# ============================================================

@admin_required
def category_list(request):

    categories = Category.objects.order_by(
        Lower("name")
    )

    return render(
        request,
        "admin_pages/category_list.html",
        {
            "categories": categories,
        },
    )


@admin_required
def add_category(request):

    form = CategoryForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Category added successfully."
        )

        return redirect(
            "category_list"
        )

    return render(
        request,
        "admin_pages/add_category.html",
        {
            "form": form,
        },
    )


@admin_required
def update_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    form = CategoryForm(
        request.POST or None,
        instance=category,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Category updated successfully."
        )

        return redirect(
            "category_list"
        )

    return render(
        request,
        "admin_pages/add_category.html",
        {
            "form": form,
            "category": category,
        },
    )


@admin_required
def delete_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    if request.method == "POST":

        category.delete()

        messages.success(
            request,
            "Category deleted successfully."
        )

    return redirect(
        "category_list"
    )






# ============================================================
# TESTIMONIALS
# ============================================================

@admin_required
def testimonial_list(request):

    testimonials = Paginator(
        Testimonial.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/review_list.html",
        {
            "testimonials": testimonials,
        },
    )


@admin_required
def testimonial_create(request):

    form = TestimonialForm(
        request.POST or None,
        request.FILES or None,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Testimonial created successfully."
        )

        return redirect(
            "review_list"
        )

    return render(
        request,
        "admin_pages/create_review.html",
        {
            "form": form,
        },
    )


@admin_required
def testimonial_update(request, pk):

    testimonial = get_object_or_404(
        Testimonial,
        pk=pk,
    )

    form = TestimonialForm(
        request.POST or None,
        request.FILES or None,
        instance=testimonial,
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Testimonial updated successfully."
        )

        return redirect(
            "review_list"
        )

    return render(
        request,
        "admin_pages/create_review.html",
        {
            "form": form,
            "testimonial": testimonial,
        },
    )


@admin_required
def testimonial_delete(request, pk):

    testimonial = get_object_or_404(
        Testimonial,
        pk=pk,
    )

    if request.method == "POST":

        testimonial.delete()

        messages.success(
            request,
            "Testimonial deleted successfully."
        )

    return redirect(
        "review_list"
    )




# ============================================================
# CONTACT MESSAGES
# ============================================================

@admin_required
def view_contacts(request):

    contacts = Paginator(
        ContactMessage.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/view_contacts.html",
        {
            "contacts": contacts,
        },
    )


@admin_required
def delete_contact(request, pk):

    contact = get_object_or_404(
        ContactMessage,
        pk=pk,
    )

    if request.method == "POST":

        contact.delete()

        messages.success(
            request,
            "Contact message deleted successfully."
        )

    return redirect(
        "view_contacts"
    )




# ============================================================
# BOOKING ENQUIRIES
# ============================================================

@admin_required
def admin_enquiry_list(request):

    enquiries = Paginator(
        BookingEnquiry.objects.order_by("-created_at"),
        10,
    ).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/enquiry_list.html",
        {
            "enquiries": enquiries,
        },
    )


@admin_required
def admin_enquiry_delete(request, pk):

    enquiry = get_object_or_404(
        BookingEnquiry,
        pk=pk,
    )

    if request.method == "POST":

        enquiry.delete()

        messages.success(
            request,
            "Booking enquiry deleted successfully."
        )

    return redirect(
        "admin_enquiry_list"
    )



# ---------------------------
# frontend
# -------------------------



def home(request):
    packages = TourPackage.objects.all()[:12]

    destinations = Destination.objects.all()

    gallery_images = (
        GalleryImage.objects
        .select_related("category")
        .order_by("-uploaded_at", "-id")[:5]
    )
    latest_blogs = Blog.objects.order_by(
          "-created_at", "-id"
         )[:2]

    testimonials = Testimonial.objects.all().order_by(
    "-created_at", "-id"
    )
    
    
    context = {
        "packages": packages,
        "destinations": destinations,
        "gallery_images": gallery_images,
        "latest_blogs": latest_blogs,
        "testimonials":testimonials,
    }

    return render(request, "frontend/home.html", context)



def about(request):
    packages = TourPackage.objects.all()[:12]
    testimonials = Testimonial.objects.all().order_by(
        "-created_at", "-id"
        )
    context = {
            "packages": packages,
            
            
            "testimonials":testimonials,
        }    
    return render(request,"frontend/about.html",context)

def services(request):
    return render(request, "frontend/services.html")


def blog(request):
    # Get blogs from database
    blog_list = Blog.objects.all()

    # Show 6 blogs per page
    paginator = Paginator(blog_list, 6)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "blogs": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
    }

    return render(
        request,
        "frontend/blog.html",
        context
    )


def blog_detail(request, slug):
    blog_post = get_object_or_404(
        Blog,
        slug=slug
    )

    # Latest blogs excluding current article
    recent_blogs = (
        Blog.objects
        .exclude(pk=blog_post.pk)
        .order_by("-created_at")[:3]
    )

    context = {
        "blog": blog_post,
        "recent_blogs": recent_blogs,
    }

    return render(
        request,
        "frontend/blog_details.html",
        context
    )



def contact(request):
    return render(request, "frontend/contact.html")


from django.shortcuts import render
from django.core.paginator import Paginator

from .models import Category, GalleryImage


def gallery(request):

    # Get selected category ID from URL
    selected_category = request.GET.get("category", "all")

    # Get all categories for filter buttons
    categories = Category.objects.all().order_by("name")

    # Get gallery images from database
    gallery_images = (
        GalleryImage.objects
        .select_related("category")
        .order_by("-uploaded_at", "-id")
    )

    # Filter images by selected category
    if selected_category != "all":

        try:
            category_id = int(selected_category)

            if category_id <= 0:
                raise ValueError

            if categories.filter(id=category_id).exists():

                gallery_images = gallery_images.filter(
                    category_id=category_id
                )

                selected_category = str(category_id)

            else:
                selected_category = "all"

        except (ValueError, TypeError):
            selected_category = "all"

    # Pagination: 9 images per page
    paginator = Paginator(gallery_images, 9)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "gallery_images": page_obj,
        "page_obj": page_obj,
        "selected_category": selected_category,
        "total_images": paginator.count,
    }

    return render(
        request,
        "frontend/gallery.html",
        context
    )



from django.shortcuts import render, get_object_or_404
from .models import TourPackage


def packages(request):
    package_type = request.GET.get("type", "all")

    valid_types = {
        "international",
        "domestic",
        "hot_selling",
    }

    packages_qs = TourPackage.objects.all()

    if package_type in valid_types:
        packages_qs = packages_qs.filter(
            package_type=package_type
        )
    else:
        package_type = "all"

    context = {
        "packages": packages_qs,
        "selected_type": package_type,
    }

    return render(
        request,
        "frontend/packages.html",
        context
    )


def package_detail(request, slug):
    package = get_object_or_404(
        TourPackage,
        slug=slug
    )

    other_packages = (
        TourPackage.objects
        .exclude(pk=package.pk)
        .order_by("-created_at")[:8]
    )

    context = {
        "package": package,
        "other_packages": other_packages,
    }

    return render(
        request,
        "frontend/package-detail.html",
        context
    )

import json
import re
import urllib.parse
import urllib.request
from urllib.parse import quote_plus

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import ContactMessage


_MAP_QUERY = "Deutsche Yathras, Berliner Str. 80, 66849 Landstuhl, Germany"

CONTACT_INFO = {
    "address_lines": [
        "Deutsche Yathras",
        "Berliner Str. 80",
        "66849 Landstuhl",
        "Germany",
    ],
    "phone": "+49 1525 9283551",
    "phone_link": "+4915259283551",
    "email": "deutscheyathras@gmail.com",
    "map_embed": f"https://www.google.com/maps?q={quote_plus(_MAP_QUERY)}&z=15&output=embed",
    "map_link": f"https://www.google.com/maps/search/?api=1&query={quote_plus(_MAP_QUERY)}",
}

# Limits taken from the ContactMessage model
NAME_MAX_LENGTH = 100    # first_name, last_name
PHONE_MAX_LENGTH = 20    # phone
EMAIL_MAX_LENGTH = 254   # EmailField default
MESSAGE_MAX_LENGTH = 2000


def valid_name(value):
    """Letters only (including accents like ü, ö), plus spaces, hyphens, apostrophes and dots."""
    if not value:
        return False
    if not re.fullmatch(r"[^\W\d_]+(?:[ .'\-][^\W\d_]+)*\.?", value):
        return False
    return True


def clean_phone(value):
    """Return the phone with separators removed (7 to 15 digits, optional leading +), else None."""
    value = re.sub(r"[\s\-().]", "", value)
    if not re.fullmatch(r"\+?\d{7,15}", value):
        return None
    return value


def verify_recaptcha(token, remote_ip=None):
    """Return True if Google confirms the reCAPTCHA token is valid."""
    if not token:
        return False

    payload = {
        "secret": settings.RECAPTCHA_SECRET_KEY,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data,
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode()).get("success", False)
    except Exception:
        return False


def contact(request):
    if request.method == "POST":
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        def fail(msg, status=400):
            if is_ajax:
                return JsonResponse({"ok": False, "error": msg}, status=status)
            messages.error(request, msg)
            return redirect("contact")

        def success():
            if is_ajax:
                return JsonResponse({"ok": True})
            messages.success(request, "Thank you! We have received your message.")
            return redirect("contact")

        # Honeypot: real visitors never fill this hidden field
        if request.POST.get("website"):
            return success()

        # reCAPTCHA check
        token = request.POST.get("g-recaptcha-response", "")
        if not verify_recaptcha(token, request.META.get("REMOTE_ADDR")):
            return fail("Please confirm that you are not a robot.")

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        # ---- Required fields (first_name, last_name, phone are required in the model) ----
        if not first_name or not last_name or not phone:
            return fail("First name, last name and phone are required.")

        # ---- Names: letters only, max 100 characters ----
        if len(first_name) > NAME_MAX_LENGTH:
            return fail(f"First name must be {NAME_MAX_LENGTH} characters or fewer.")
        if len(last_name) > NAME_MAX_LENGTH:
            return fail(f"Last name must be {NAME_MAX_LENGTH} characters or fewer.")

        if not valid_name(first_name):
            return fail("First name should contain letters only, no numbers.")

        if not valid_name(last_name):
            return fail("Last name should contain letters only, no numbers.")

        # ---- Phone: 7 to 15 digits, optional leading + (fits the 20-char field) ----
        clean = clean_phone(phone)
        if not clean or len(clean) > PHONE_MAX_LENGTH:
            return fail("Please enter a valid phone number (7 to 15 digits).")
        phone = clean

        # ---- Email (optional in the model, but must be valid if given) ----
        if email:
            if len(email) > EMAIL_MAX_LENGTH:
                return fail("Email address is too long.")
            try:
                validate_email(email)
            except ValidationError:
                return fail("Please enter a valid email address.")

        # ---- Message (optional in the model) ----
        message = message[:MESSAGE_MAX_LENGTH]

        # 1) Save first so the enquiry is never lost
        try:
            ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email or None,
                message=message,
            )
        except Exception:
            return fail("Could not save your message. Please try again.", 500)

        # 2) Email notification (a failure here must not hide the saved enquiry)
        body = (
            "New contact message from the website\n\n"
            f"Name: {first_name} {last_name}\n"
            f"Phone: {phone}\n"
            f"Email: {email or '-'}\n\n"
            f"Message:\n{message or '-'}\n"
        )
        recipient = getattr(
            settings,
            "CONTACT_NOTIFY_EMAIL",
            getattr(settings, "BOOKING_NOTIFY_EMAIL", settings.DEFAULT_FROM_EMAIL),
        )
        try:
            send_mail(
                subject=f"Contact enquiry - {first_name} {last_name}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception:
            pass

        return success()

    return render(request, "frontend/contact.html", {
        "info": CONTACT_INFO,
        "recaptcha_site_key": getattr(settings, "RECAPTCHA_SITE_KEY", ""),
    })
from django.shortcuts import render, get_object_or_404
from .models import Destination


def destinations(request):
    destination_type = request.GET.get("type", "all")

    valid_types = {
        Destination.DOMESTIC,
        Destination.INTERNATIONAL,
    }

    if destination_type not in valid_types:
        destination_type = "all"

    destination_list = Destination.objects.all()

    if destination_type != "all":
        destination_list = destination_list.filter(
            destination_type=destination_type
        )

    context = {
        "destinations": destination_list,
        "selected_type": destination_type,
        "total_destinations": destination_list.count(),
    }

    return render(
        request,
        "frontend/destinations.html",
        context
    )


def destination_detail(request, slug):
    destination = get_object_or_404(
        Destination,
        slug=slug
    )

    related_destinations = (
        Destination.objects
        .filter(destination_type=destination.destination_type)
        .exclude(pk=destination.pk)[:4]
    )

    context = {
        "destination": destination,
        "related_destinations": related_destinations,
    }

    return render(
        request,
        "frontend/destination_detail.html",
        context
    )

from django.http import JsonResponse


def booking(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        package_id = request.POST.get("package", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        travelers = request.POST.get("travelers", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([name, email, phone, package_id, start_date, end_date, travelers]):
            return JsonResponse(
                {"success": False, "message": "Please fill in all required fields."},
                status=400,
            )

        if end_date < start_date:
            return JsonResponse(
                {"success": False, "message": "End date cannot be before the start date."},
                status=400,
            )

        try:
            package = TourPackage.objects.get(pk=package_id)
        except (TourPackage.DoesNotExist, ValueError):
            return JsonResponse(
                {"success": False, "message": "Please select a valid package."},
                status=400,
            )

        model_fields = {f.name: f for f in BookingEnquiry._meta.get_fields()}

        def pick(names):
            for n in names:
                if n in model_fields:
                    return n
            return None

        data = {}

        for value, names in [
            (name, ["name", "full_name"]),
            (email, ["email"]),
            (phone, ["phone", "phone_number", "mobile"]),
            (start_date, ["start_date", "travel_date", "from_date", "check_in", "date"]),
            (end_date, ["end_date", "to_date", "return_date", "check_out"]),
            (travelers, ["adults", "travelers", "guests", "persons", "no_of_persons", "number_of_travelers"]),
        ]:
            field = pick(names)
            if field:
                data[field] = value

        # Children (only if the model has this field and the form doesn't send it)
        if "children" in model_fields and "children" not in data:
            data["children"] = 0

        # Package: store the object if the field is a ForeignKey, otherwise the name
        package_field = pick(["package", "tour_package", "package_name", "destination", "trip"])
        if package_field:
            if model_fields[package_field].is_relation:
                data[package_field] = package
            else:
                data[package_field] = str(package)

        # Message (also keeps the end date if the model has no end-date field yet)
        message_field = pick(["message", "notes", "comments"])
        if message_field:
            extra = "" if pick(["end_date", "to_date", "return_date", "check_out"]) else f"End date: {end_date}\n"
            data[message_field] = f"{extra}{message}".strip()

        try:
            BookingEnquiry.objects.create(**data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("DATA SENT TO MODEL:", data)
            return JsonResponse(
                {"success": False, "message": f"Could not save: {e}"},
                status=500,
            )

        return JsonResponse(
            {"success": True, "message": "Thank you! We will contact you shortly."}
        )

    return render(request, "frontend/booking.html")





