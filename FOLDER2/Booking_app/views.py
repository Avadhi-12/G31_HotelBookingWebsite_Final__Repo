from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import BookingForm
from .models import Booking
from hotel_app.models import Hotel, Room


@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'booking_app/booking_form.html', {'form': form})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    context = {'bookings': bookings}
    now = timezone.now()

    
    return render(request, 'booking_app/my_bookings.html', {'bookings': bookings})

@login_required
def book_room(request, hotel_id, room_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    room = get_object_or_404(Room, id=room_id)

    # Check if the room is available
    if not room.available:
        messages.error(request, "Sorry, this room is already booked.")
        return redirect('hotel_detail', hotel_id=hotel_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, hotel_id=hotel_id)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.room = room

            # Check-in and check-out validation
            if booking.check_in < timezone.now().date():
                messages.error(request, "Check-in cannot be in the past.")
                return redirect('book_room', hotel_id=hotel_id, room_id=room_id)

            if booking.check_out <= booking.check_in:
                messages.error(request, "Check-out must be after check-in.")
                return redirect('book_room', hotel_id=hotel_id, room_id=room_id)

            booking.status = 'Pending'
            booking.save()

            # Optionally set booking_id in session for later use (like payment)
            request.session['booking_id'] = booking.id
            return redirect('payment_page')

    else:
        form = BookingForm(hotel_id=hotel_id)

    return render(request, 'booking_app/book_room.html', {
        'form': form,
        'hotel': hotel,
        'room': room,
    })



@staff_member_required
def admin_dashboard(request):
    hotels = Hotel.objects.all()
    pending_cancellations = Booking.objects.filter(cancellation_status='pending')
    bookings = Booking.objects.all()
    return render(request, 'hotel_app/admin_dashboard.html', {
        'hotels': hotels,
        'pending_cancellations': pending_cancellations,
        'bookings': bookings,
    })


@staff_member_required
def admin_all_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'booking_app/admin_all_bookings.html', {'bookings': bookings})


@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.check_in = request.POST.get('check_in')
        booking.check_out = request.POST.get('check_out')
        booking.save()
        messages.success(request, "Booking updated successfully.")
        return redirect('admin_all_bookings')
    return render(request, 'booking_app/update_booking.html', {'booking': booking})


@staff_member_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.room.available = True
        booking.room.save()
        booking.delete()
        messages.success(request, "Booking deleted.")
        return redirect('admin_all_bookings')
    return render(request, 'booking_app/delete_booking.html', {'booking': booking})


@login_required
def update_booking_user(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    check_in_datetime = timezone.make_aware(datetime.combine(booking.check_in, datetime.min.time()))
    if check_in_datetime - timezone.now() < timedelta(hours=24):
        messages.error(request, "You cannot update this booking within 24 hours of check-in.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully.')
            return redirect('my_bookings')
        else:
            messages.error(request, 'Please fix the errors in the form.')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'booking_app/update_booking_user.html', {'form': form})


@login_required
def delete_booking_user(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check 24-hour rule
    check_in_datetime = timezone.make_aware(datetime.combine(booking.check_in, datetime.min.time()))
    if check_in_datetime - timezone.now() < timedelta(hours=24):
        messages.error(request, "You cannot cancel this booking within 24 hours of check-in.")
        return redirect('my_bookings')

    if request.method == 'POST':
        # Delete booking and mark room available
        booking.room.available = True
        booking.room.save()
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my_bookings')

    return render(request, 'booking_app/delete_booking.html', {'booking': booking})

@login_required
def request_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    check_in_datetime = timezone.make_aware(datetime.combine(booking.check_in, datetime.min.time()))
    if check_in_datetime - timezone.now() > timedelta(hours=24):
        booking.cancellation_status = 'pending'  # Correctly set cancellation status to 'pending'
        booking.save()
        messages.success(request, "Your cancellation request has been submitted and is pending approval.")
    else:
        messages.error(request, "You can only request cancellation more than 24 hours before check-in.")

    return redirect('my_bookings')



@staff_member_required
def approve_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.cancellation_status = 'approved'
        booking.room.available = True
        booking.room.save()
        booking.save()
        messages.success(request, 'Booking cancellation approved.')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


@staff_member_required
def decline_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.cancellation_status = 'declined'
        booking.save()
        messages.info(request, 'Cancellation request declined.')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    if booking.status != 'Cancelled' and booking.cancellation_status == 'none':
        # Submit cancellation request
        booking.request_cancellation()
        messages.success(request, 'Cancellation request submitted successfully. Admin will review it shortly.')
    else:
        messages.error(request, 'This booking has already been cancelled or cancellation is pending.')
    
    return redirect('my_bookings') 


@staff_member_required
def admin_cancellation_requests(request):
    # Ensure that you're filtering bookings with 'pending' status
    pending_cancellations = Booking.objects.filter(cancellation_status='pending')
    return render(request, 'booking_app/admin_cancellation_requests.html', {
        'pending_cancellations': pending_cancellations
    })



@staff_member_required
def approve_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.cancellation_status = 'approved'  # ✅ Correct field
        booking.room.available = True
        booking.room.save()
        booking.save()
        messages.success(request, 'Booking cancellation approved.')
    return redirect('admin_dashboard')

@staff_member_required
def decline_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.cancellation_status = 'declined'  # ✅ Correct field
        booking.save()
        messages.info(request, 'Cancellation request declined.')
    return redirect('admin_dashboard')


def manage_cancellations(request):
    if not request.user.is_staff:
        return redirect('home')  # Redirect if the user is not an admin

    cancellation_requests = Booking.objects.filter(cancellation_status='pending')
    
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = Booking.objects.get(id=booking_id)
        
        if action == 'approve':
            booking.approve_cancellation()
            messages.success(request, 'Cancellation request approved.')
        elif action == 'reject':
            booking.decline_cancellation()
            messages.success(request, 'Cancellation request rejected.')
    
    return render(request, 'booking_app/manage_cancellations.html', {'cancellation_requests': cancellation_requests})

def debug_pending_cancellations(request):
    bookings = Booking.objects.filter(cancellation_status='pending')
    output = "\n".join([f"{b.user} - {b.hotel} - {b.cancellation_status}" for b in bookings])
    return HttpResponse(output or "No pending bookings")



@login_required
def payment_page(request):
    booking_id = request.session.get('booking_id')
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        method = request.POST.get('method')
        # Simulate payment success
        booking.status = 'Confirmed'
        booking.room.available = False
        booking.room.save()
        booking.save()

        del request.session['booking_id']  # Clear session after use

        messages.success(request, f"Payment successful via {method}. Booking confirmed!")
        return redirect('my_bookings')

    return render(request, 'booking_app/payment.html')



