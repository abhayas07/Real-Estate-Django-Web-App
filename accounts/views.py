from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login  # Import login as auth_login
from django.urls import reverse_lazy
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Contact  # Import the Contact model

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            # Show error message if username is taken
            messages.error(request, "Username is already taken. Please choose another.")
            return redirect('register')  # Redirect back to registration page
        else:
            # Create the user
            user = User.objects.create_user(username=username, password=password)
            # Log the user in correctly
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful registration
    
    return render(request, 'accounts/register.html')
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Correct usage: pass both 'request' and 'user'
            # Redirect to the Django admin page after successful login
            return redirect(reverse_lazy('dashboard'))  # This will take the user to the Django admin interface
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')  # Redirect back to login page if authentication fails

    return render(request, 'accounts/login.html')
def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')

def dashboard(request):
    if request.user.is_authenticated:
        # Retrieve contacts for the logged-in user, ordered by contact date
        user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)
        return render(request, 'accounts/dashboard.html', {'contacts': user_contacts})
    return redirect('login')  # Redirect to login page if the user is not authenticated
