from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel, Room, Review
from booking_app.models import Booking
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q
from .forms import HotelForm, RoomForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ReviewForm
# -------------------- Public Views --------------------

def home_view(request):
    return render(request, 'home.html')

def hotel_list(request):
    hotels = Hotel.objects.all().prefetch_related('rooms')

    location = request.GET.get('location')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    room_type = request.GET.getlist('room_type')
    wifi = request.GET.get('wifi')
    pool = request.GET.get('pool')
    parking = request.GET.get('parking')

    if location:
        hotels = hotels.filter(location__icontains=location)

    if max_price:
        hotels = hotels.filter(price_per_night__lte=max_price)

    if rating:
        hotels = hotels.filter(rating__gte=rating)

    if room_type:
        hotels = hotels.filter(room_type=room_type)

    if wifi:
        hotels = hotels.filter(amenities__icontains='wifi')

    if pool:
        hotels = hotels.filter(amenities__icontains='pool')

    if parking:
        hotels = hotels.filter(amenities__icontains='parking')

    for hotel in hotels:
        hotel.available_rooms = hotel.rooms.filter(available=True)


    return render(request, 'hotel_app/hotel_list.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.filter(available=True)
    return render(request, 'hotel_app/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms
    })


def admin_required(view_func):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff)(view_func)


# -------------------- Admin Views --------------------

def is_admin(user):
    return user.is_staff

def admin_dashboard(request):
    # Fetching all bookings and filtering for pending cancellation requests
    bookings = Booking.objects.all()
    pending_cancellations = bookings.filter(cancellation_status='pending')
    hotels = Hotel.objects.all()
    
    return render(request, 'admin_dashboard.html', {
        'hotels': hotels,
        'bookings': bookings,
        'pending_cancellations': pending_cancellations  # Pass pending cancellations separately
    })

@user_passes_test(is_admin)
def add_hotel(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = HotelForm()
    return render(request, 'hotel_app/hotel_form.html', {'form': form, 'title': 'Add Hotel'})

@user_passes_test(is_admin)
def update_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'hotel_app/hotel_form.html', {'form': form, 'title': 'Update Hotel'})

@user_passes_test(is_admin)
def delete_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    hotel.delete()
    return redirect('admin_dashboard')

# -------------------- Room Management --------------------

@user_passes_test(is_admin)
def manage_rooms(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.all()
    return render(request, 'hotel_app/manage_rooms.html', {
        'hotel': hotel,
        'rooms': rooms
    })

@user_passes_test(is_admin)
def add_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            return redirect('manage_rooms', hotel_id=hotel.id)
    else:
        form = RoomForm()
    return render(request, 'hotel_app/room_form.html', {'form': form, 'hotel': hotel, 'title': 'Add Room'})

@user_passes_test(is_admin)
def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('manage_rooms', hotel_id=room.hotel.id)
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotel_app/room_form.html', {'form': form, 'title': 'Update Room'})

@user_passes_test(is_admin)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    hotel_id = room.hotel.id
    if request.method == 'POST':
        room.delete()
        return redirect('manage_rooms', hotel_id=hotel_id)
    return render(request, 'hotel_app/confirm_delete.html', {'object': room, 'type': 'Room'})



@login_required
def add_review(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.hotel = hotel
            review.save()
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = ReviewForm()
    return render(request, 'hotel_app/add_review.html', {'form': form, 'hotel': hotel})
















