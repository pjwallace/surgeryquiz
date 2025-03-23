
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("learners.urls")),
    path("quizes/home/", include("quizes.urls")),
    path("management/portal/", include("management.urls")),
]
