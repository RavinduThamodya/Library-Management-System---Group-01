from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Reservation
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Book
from django.utils.timezone import make_aware
from datetime import datetime, time
# =======================
# Authentication Views
# =======================

#landing page view
def landing_page(request):
    """Public landing page."""
    return render(request, 'landing.html')

#register view
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

#log in view
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

#Home page view
@login_required
def home(request):
    categories = Book.objects.values('category').annotate(book_count=Count('id')).distinct()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q')

    books = []

    # Handle search query
    if search_query:
        books = Book.objects.filter(
            Q(title__icontains=search_query) | Q(author__icontains=search_query)
        )
    elif selected_category:
        books = Book.objects.filter(category=selected_category)

    # If both category and search query are present, combine them
    if selected_category and search_query:
        books = books.filter(category=selected_category)

    # Get trending books this week
    trending_books_data = trending_books(request)

    return render(request, 'home.html', {
        'categories': categories,
        'books': books,
        'selected_category': selected_category,
        'search_query': search_query,
        'trending_books': trending_books_data  # Pass trending books to the template
    })

#my reservations list
@login_required
def my_reservations(request):
    # Assuming you have a ForeignKey relationship with User in the Reservation model
    reservations = Reservation.objects.filter(user=request.user)  # Filter by the logged-in user

    for reservation in reservations:
        # Calculate collecting week by adding 7 days to reservation date
        reservation.collecting_week = reservation.reservation_date + timedelta(days=7)

    return render(request, 'my_reservations.html', {'reservations': reservations})
# =======================
# Reservation Views
# =======================

#cancel reservations
@login_required
def cancel_reservation(request, book_id):
    """
    Allows a user to cancel their own reservation.
    Updates book status, increases available count, and shows a confirmation message.
    """
    reservation = Reservation.objects.filter(book_id=book_id, user=request.user).first()

    if reservation:
        book = reservation.book
        book.is_reserved = False


        book.total_copies += 1

        book.save()
        reservation.delete()
        messages.info(request, f"You have cancelled your reservation for '{book.title}'.")
    else:
        messages.warning(request, "No reservation found to cancel.")

    return redirect('my_reservations')

#reserve books
@login_required
def reserve_book(request, book_id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, id=book_id)

        # Check if the user already reserved this book
        existing_reservation = Reservation.objects.filter(user=request.user, book=book).first()
        if existing_reservation:
            messages.error(request, "You have already reserved this book.")
            return redirect('home')  # or wherever you want to redirect

        # Check if copies are available
        if book.total_copies > 0:
            # Create the reservation
            reservation = Reservation.objects.create(user=request.user, book=book)

            # Calculate collecting week (1 week after reservation date)
            collecting_week = reservation.reservation_date + timedelta(weeks=1)
            print(f"Calculated Collecting Week: {collecting_week}")
            reservation.collecting_week = collecting_week
            reservation.save()


            # Reduce the available copies of the book
            book.total_copies -= 1
            book.save()

            messages.success(request, "Book reserved successfully!")
        else:
            messages.error(request, "No copies available for reservation.")

        return redirect('home')  # Redirect back to the home page or other relevant page



#fetch book details 
def book_detail(request, book_id):
    # Get the book object for the clicked book
    book = get_object_or_404(Book, id=book_id)

    # Fetch related books by category or author
    related_books = Book.objects.filter(
        category=book.category
    ).exclude(id=book.id)[:4]  # Exclude the current book and limit to 4 books

    # You could also use author-based filtering or other criteria
    # related_books = Book.objects.filter(author=book.author).exclude(id=book.id)[:4]

    return render(request, 'book_detail.html', {
        'book': book,
        'related_books': related_books
    })

#about us webpage
def about_us(request):
    return render(request, 'about_us.html')


#show trending books for the week
def trending_books(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=7)
    end_date = today

    # Convert date range to datetime range
    start_datetime = make_aware(datetime.combine(start_date, time.min))
    end_datetime = make_aware(datetime.combine(today, time.max))

    trending_books = (
        Book.objects
        .annotate(
            reservation_count=Count(
                'reservation',
                filter=Q(reservation__reservation_date__range=[start_datetime, end_datetime])
            )
        )
        .filter(reservation_count__gt=0)
        .order_by('-reservation_count')[:4]
    )

    return trending_books
