from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RealtorLoginForm, RealtorRegisterForm  # Import forms for login and register

# Realtor Login View
def realtor_login(request):
    if request.method == 'POST':
        form = RealtorLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard or another page
            else:
                form.add_error(None, "Invalid credentials")
    else:
        form = RealtorLoginForm()
    
    return render(request, 'realtor/realtor_login.html', {'form': form})

# Realtor Register View
def realtor_register(request):
    if request.method == 'POST':
        form = RealtorRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('realtor-login')  # Redirect to login after successful registration
    else:
        form = RealtorRegisterForm()
    
    return render(request, 'realtor/realtor_register.html', {'form': form})
