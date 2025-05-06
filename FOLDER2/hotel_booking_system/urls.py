from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Use only one of these:
    path('admin/', admin.site.urls),  # Standard Django admin panel path
    # path('site-admin/', admin.site.urls),  # Optional: use this if you want a custom admin URL

    # Auth App Routes (don't duplicate)
    path('', include('auth_app.urls')),

    # Other app routes
    path('hotels/', include('hotel_app.urls')),
    path('booking/', include('booking_app.urls')),
    path('user/', include('user_app.urls')),
]

# Static/media files handling in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
