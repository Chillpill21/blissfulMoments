from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart

def search(request):
    # Determine if they filled out the form
    if request.method == 'POST':
        searched  = request.POST['searched']
        # Query the Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.success(request, "That Product Does not exist!!")
            return render(request,'search.html', {})
        else:
            return render(request,'search.html', {'searched':searched})
    else:
        return render(request,'search.html', {})

def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id = request.user.id)
        # Get current user's Shipping Info
        shipping_user = ShippingAddress.objects.get(id=request.user.id)
        # Get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # Get User's Shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your Info has been Updated!!")
            return redirect('index')
        return render(request, "update_info.html", {"form": form, 'shipping_form':shipping_form})
    else:
        messages.success(request, "You must be logged in first!!")
        return redirect('index')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password has been Updated!, Please Login again!!")
                # login(request, current_user)
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form  = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.success(request, "You Must be Logged in to view that!")
        return redirect('index')


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id = request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User has been Updated!!")
            return redirect('index')
        return render(request, "update_user.html", {"user_form": user_form})
    else:
        messages.success(request, "You must be logged in first!!")
        return redirect('index')
    

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})

def category(request, foo):
    foo = foo.replace('-',' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(catregory=category)
        return render(request,'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("The Category does not exist please try again."))
        return redirect('index')

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product
    })

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products':products
    })

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from db
            saved_cart = current_user.old_cart
            # Convert db str to dict
            if saved_cart:
                # Convert to dict using json
                converted_cart = json.loads(saved_cart)
                # Add loaded dict to session
                # Get the cart
                cart = Cart(request)
                # Loop thrgh cart and add the items from the db
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            messages.success(request, ("You have been logged in."))
            return redirect('index')
        
        else:
            messages.success(request, ("There was an error please try again."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out."))
    return redirect('index')

def register_user(request):
    form  = SignUpForm()
    if request.method == 'POST':
        form  = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have Registered successfully -Please fill your info below..."))
            return redirect('update_info')
        else:
            messages.success(request, ('Whoops! There was a problem registering please try again!'))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})