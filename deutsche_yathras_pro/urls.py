from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Django built-in admin
    path(
        "django-admin/",
        admin.site.urls,
    ),

    # Malabar Tours website/admin
    path(
        "",
        include("deutsche_yathras_app.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

handler404 = "deutsche_yathras_app.views.custom_404"