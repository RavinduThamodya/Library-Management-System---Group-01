from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('cancel/<int:book_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('about_us/', views.about_us, name='about_us'),
]
