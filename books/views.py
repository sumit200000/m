from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Cart
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Book, Cart, Review
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.core.mail import send_mail
from .models import Order, OrderItem
from .models import Book, Wishlist
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import Book, Category
from django.db.models import Count
from django.db.models import Count, Q
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.http import JsonResponse
from .forms import NewsletterSubscriptionForm
from django.shortcuts import redirect
from django.contrib import messages
from .models import Cart
from .models import  Cart, CartItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Book, Cart, CartItem
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm





def home(request):
    featured_books = Book.objects.filter(featured=True)[:5]
    bestsellers = Book.objects.annotate(num_orders=Count('orderitem')).order_by('-num_orders')[:4]
    new_arrivals = Book.objects.order_by('-created_at')[:4]
    testimonials = Review.objects.filter(rating__gte=4).order_by('-created_at')[:3]
    return render(request, 'books/index.html', {
        'featured_books': featured_books,
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'testimonials': testimonials,
    })

def product_listing(request):
    books = Book.objects.all()
    categories = Category.objects.all()
    category_filter = request.GET.get('category')
    if category_filter:
        books = books.filter(category__id=category_filter)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min and price_max:
        books = books.filter(price__gte=price_min, price__lte=price_max)
    return render(request, 'books/product_listing.html', {'books': books, 'categories': categories})


def product_detail(request, id):
    book = get_object_or_404(Book, pk=id)
    reviews = Review.objects.filter(book=book)
    recommendations = Book.objects.annotate(num_reviews=Count('review')).order_by('-num_reviews')[:4]  # Example logic
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('product_detail', id=book.id)
    else:
        form = ReviewForm()
    return render(request, 'books/product_detail.html', {'book': book, 'reviews': reviews, 'form': form, 'recommendations': recommendations})

def cart(request):
    cart = Cart.objects.all()
    return render(request, 'books/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    return render(request, 'books/cart.html', {'cart_items': cart_items})

@login_required
def remove_from_cart(request, book_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, book_id=book_id)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            payment = form.cleaned_data['payment']

            # Create order
            order = Order.objects.create(user=request.user, name=name, address=address, payment_method=payment)
            
            for item in cart_items:
                OrderItem.objects.create(order=order, book=item.book, quantity=item.quantity, price=item.book.price)
            
            # Clear the cart
            cart_items.delete()

            return redirect('order_complete')
    else:
        form = CheckoutForm()

    return render(request, 'books/checkout.html', {'form': form, 'cart_items': cart_items})
# books/views.py
@login_required
def complete_order(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    # Logic to create an order from the cart items
    # For example, save order to database, process payment, etc.
    cart_items.delete()  # Clear the cart after order is completed
    return render(request, 'books/order_complete.html')


def buy_product(request):
    return render(request, 'books/buy_product.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user but don't save to the database yet
            new_user = form.save(commit=False)
            # Set the chosen password
            new_user.set_password(form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Log the user in
            user = authenticate(username=new_user.username, password=form.cleaned_data['password'])
            login(request, user)
            return redirect('home')  # Redirect to home page or another page
    else:
        form = UserRegistrationForm()
    return render(request, 'books/register.html', {'form': form})

def product_detail(request, id):
    book = get_object_or_404(Book, pk=id)
    reviews = Review.objects.filter(book=book)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('product_detail', id=book.id)
    else:
        form = ReviewForm()
    return render(request, 'books/product_detail.html', {'book': book, 'reviews': reviews, 'form': form})

def search(request):
    query = request.GET.get('q')
    books = Book.objects.filter(title__icontains=query)
    return render(request, 'books/product_listing.html', {'books': books})

@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    return redirect('wishlist')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    paginator = Paginator(wishlist_items, 10)  # Show 10 items per page
    page = request.GET.get('page')
    try:
        wishlist_items = paginator.page(page)
    except PageNotAnInteger:
        wishlist_items = paginator.page(1)
    except EmptyPage:
        wishlist_items = paginator.page(paginator.num_pages)
    return render(request, 'books/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'books/profile.html', {'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'books/order_history.html', {'orders': orders})

def update_order_status(order, status):
    order.status = status
    order.save()
    send_mail(
        f'Order {order.id} Status Update',
        f'Your order status has been updated to {status}.',
        'from@example.com',
        [order.user.email],
        fail_silently=False,
    )
@staff_member_required
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()
    delivered_orders = Order.objects.filter(status='Delivered').count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
    }
    
    return TemplateResponse(request, 'admin/order_change_list.html', context)

def subscribe(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Subscribed successfully!'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'message': 'Invalid request'}, status=400)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page, such as the home page
            return redirect('home')
        else:
            # Invalid login, display an error message
            messages.error(request, 'Invalid username or password.')
    # If request method is GET or authentication fails, render the login form
    return render(request, 'books/login.html')

def user_logout(request):
     if request.method == 'POST':
        logout(request)
        # Redirect to the home page after logout
        return redirect('home')
     return render(request, 'books/logout.html')
   
from django.db.models import Sum
from django.shortcuts import render
from .models import Order

# def my_view(request):
#     # Perform aggregation
#     total_price = Order.objects.aggregate(total=Sum('items__price'))['total']
#     # Pass the aggregated value to the template
#     return render(request, 'my_template.html', {'total_price': total_price})
