from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('hotels/', views.hotel_list, name='hotel_list'),

    # Hotel CRUD
    path('dashboard/hotel/add/', views.add_hotel, name='add_hotel'),
    path('dashboard/hotel/<int:hotel_id>/update/', views.update_hotel, name='update_hotel'),
    path('dashboard/hotel/<int:hotel_id>/delete/', views.delete_hotel, name='delete_hotel'),

    # Room CRUD
    path('dashboard/hotel/<int:hotel_id>/rooms/', views.manage_rooms, name='manage_rooms'),
    path('dashboard/hotel/<int:hotel_id>/room/add/', views.add_room, name='add_room'),
    path('dashboard/room/<int:room_id>/update/', views.update_room, name='update_room'),
    path('dashboard/room/<int:room_id>/delete/', views.delete_room, name='delete_room'),

    # Hotel detail
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('hotel/<int:hotel_id>/review/', views.add_review, name='add_review'),
    path('hotels/', views.hotel_list, name='get_hotels'),

]
