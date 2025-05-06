from django.contrib import admin
from django.urls import path, include
from . import views
from .views import admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include app-specific urls
    path('', include('auth_app.urls')),
    path('hotels/', include('hotel_app.urls')),
    path('user/', include('user_app.urls')),

    # Booking-related views
    path('book-room/<int:hotel_id>/<int:room_id>/', views.book_room, name='book_room'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/update/<int:booking_id>/', views.update_booking_user, name='update_booking_user'),
    path('my-bookings/delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Admin dashboard & booking management
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/bookings/', views.admin_all_bookings, name='admin_all_bookings'),
    path('booking/<int:booking_id>/update/', views.update_booking, name='update_booking'),  # For admin
    path('booking/delete/<int:booking_id>/', views.delete_booking_user, name='delete_booking_user'),  # For admin

    # Cancellation workflow (for users)
    path('booking/<int:booking_id>/request-cancel/', views.request_cancellation, name='request_cancellation'),

    # Admin handles cancellation requests
    path('cancel/approve/<int:booking_id>/', views.approve_cancellation, name='approve_cancellation'),
    path('cancel/decline/<int:booking_id>/', views.decline_cancellation, name='decline_cancellation'),
    path('admin/manage-cancellations/', views.manage_cancellations, name='manage_cancellations'),

    path('payment/', views.payment_page, name='payment_page'),

    

]
