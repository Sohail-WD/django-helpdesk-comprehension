from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from demo import views as demo_views

urlpatterns = [
    # Clean role-oriented entry points for the demo.
    path("", demo_views.home, name="demo-home"),
    path("customer/", demo_views.customer_entry, name="customer-entry"),
    path("agent/", demo_views.agent_entry, name="agent-entry"),
    path("manager/", demo_views.manager_entry, name="manager-entry"),

    path(
        "helpdesk/logout/",
        demo_views.logout_view,
        name="demo-logout",
    ),
    
    # The host project exposes the reusable django-helpdesk application here.
    path("helpdesk/", include("helpdesk.urls", namespace="helpdesk")),

    # Django admin remains available for the manager role.
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
