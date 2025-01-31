from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("Inventory/", include("Inventory.urls")),
    # path("Sales/", include("Sales.urls")),
]
