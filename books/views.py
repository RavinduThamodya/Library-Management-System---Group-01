from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Book, Reservation


# =======================
# Authentication Views
# =======================

def landing_page(request):
    """Public landing page."""
    return render(request, 'landing.html')


def register(request):
    """Handles user registration."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Handles user login."""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    return render(request, 'registration/login.html')


def logout_view(request):
    """Logs the user out and redirects to login."""
    logout(request)
    return redirect('login')


# =======================
# Book Views
# =======================

@login_required
def home(request):
    """
    Displays available and reserved books.
    Allows filtering by title, author, or category.
    Separates books reserved by current user and others.
    """
    query = request.GET.get('q')
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__icontains=query)
        )

    available_books = books.filter(is_reserved=False)
    reserved_books = books.filter(is_reserved=True)

    # Get IDs of books reserved by the logged-in user
    user_reserved_book_ids = Reservation.objects.filter(user=request.user).values_list('book_id', flat=True)

    reserved_by_user = reserved_books.filter(id__in=user_reserved_book_ids)
    reserved_by_others = reserved_books.exclude(id__in=user_reserved_book_ids)

    context = {
        'available_books': available_books,
        'reserved_by_user': reserved_by_user,
        'reserved_by_others': reserved_by_others,
    }

    return render(request, 'home.html', context)


@login_required
def my_reservations(request):
    """Displays books reserved by the current user."""
    reservations = Reservation.objects.filter(user=request.user).select_related('book')
    return render(request, 'my_reservations.html', {'reservations': reservations})


# =======================
# Reservation Views
# =======================

@login_required
def reserve_book(request, book_id):
    """
    Allows a user to reserve a book if it's not already reserved.
    Updates book status and shows a success or warning message.
    """
    book = get_object_or_404(Book, id=book_id)

    if not book.is_reserved:
        Reservation.objects.create(user=request.user, book=book)
        book.is_reserved = True
        book.save()
        messages.success(request, f"You have successfully reserved '{book.title}'.")
    else:
        messages.warning(request, f"'{book.title}' is not available for reservation.")

    return redirect('home')


@login_required
def cancel_reservation(request, book_id):
    """
    Allows a user to cancel their own reservation.
    Updates book status and shows a confirmation message.
    """
    reservation = Reservation.objects.filter(book_id=book_id, user=request.user).first()

    if reservation:
        reservation.book.is_reserved = False
        reservation.book.save()
        reservation.delete()
        messages.info(request, f"You have cancelled your reservation for '{reservation.book.title}'.")
    else:
        messages.warning(request, "No reservation found to cancel.")

    return redirect('my_reservations')
