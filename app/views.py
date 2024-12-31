from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.models import User
import re
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from .models import Customer
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def home(request):
    products = Products.objects.all() 
    paginator = Paginator(products, 6)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  
    return render(request, 'home.html', {'page_obj': page_obj} )
   

def register(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        contact_number = request.POST.get("contact_number")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not re.fullmatch(r"^\d{10}$", contact_number):
            messages.error(request, "Contact number must be exactly 10 digits.")
            return redirect("register")

        if not re.fullmatch(r"^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            messages.error(request, "Password must be at least 8 characters long, include 1 uppercase letter, and 1 special character.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect("register")

        # Create a new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password  # Django automatically hashes it
        )

        # Create the associated Customer1 instance
        Customer.objects.create(
            user=user,
            customer_name=customer_name,
            contact_number=contact_number,
            email=email,
            password=make_password(password)  # Optional; you can skip this if using only `User`
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")

    return render(request, "register.html")




from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        

        # Use Django's authenticate function
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Log the user in
            auth_login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("home")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("login")

    return render(request, "login.html")


# Logout View
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def product_details(request, product_id):
    products = get_object_or_404(Products, id=product_id)
     
    return render(request, 'product_details.html', {'products': products})

def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        
        products = get_object_or_404(Products, id=product_id)
        
      
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=products)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

      
        return redirect('view_cart')
    else:
       
        messages.error(request, "Please log in to add items to the cart.")
        return redirect('login')


def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        return render(request, 'cart.html', {'cart_items': cart_items})
    else:
        messages.error(request, "Please log in to view your cart.")
        return redirect('login')
    


def increment_quantity(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('view_cart')
    else:
        messages.error(request, "Please log in to update the cart.")
        return redirect('login')

def decrement_quantity(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete() 
        return redirect('view_cart')
    else:
        messages.error(request, "Please log in to update the cart.")
        return redirect('login')


def delete_from_cart(request, cart_item_id):
    if request.user.is_authenticated:
        try:
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            cart_item.delete()
            messages.success(request, "Item removed from the cart.")
        except Cart.DoesNotExist:
            messages.error(request, "Item not found in your cart.")
    else:
        messages.error(request, "Please log in to manage your cart.")
    return redirect('view_cart') 

def search_products(request):
    query = request.GET.get('q', '') 
    products = Products.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)  
        )
    
    return render(request, 'search_results.html', {'products': products, 'query': query})

def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Products, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if created:
            messages.success(request, f"{product.name} has been added to your wishlist.")
        else:
            messages.info(request, f"{product.name} is already in your wishlist.")
    else:
       
        messages.error(request, "Please log in to add items to the wishlist.")
        return redirect('login')

    return redirect('wishlist')

@login_required
def view_wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})
    else:
        messages.error(request, "Please log in to view your cart.")
        return redirect('login')
    
    

@login_required
def remove_from_wishlist(request, wishlist_item_id):
    if request.user.is_authenticated:
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id, user=request.user)
        wishlist_item.delete()
        messages.success(request, "Item has been removed from your wishlist.")
    else:
        messages.error(request, "Please log in to manage your wishlist.")
    
    return redirect('wishlist')



