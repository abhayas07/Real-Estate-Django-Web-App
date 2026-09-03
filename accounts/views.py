import csv

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import Contact
from listings.models import Listing, Review, CsvImport
from listings.services import parse_listing_csv
from realtors.models import Realtor


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not (username and password and password2 and email):
            messages.error(request, 'Please fill in all required fields.')
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'That username is already taken. Please choose another.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'That email is already registered. Please use another.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
                return redirect('register')

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            auth.login(request, user)
            messages.success(request, 'You are now registered and logged in')
            return redirect('dashboard')

        return redirect('register')

    return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('index')
    return redirect('index')


def dashboard(request):
    if request.user.is_authenticated:
        # Retrieve contacts for the logged-in user, ordered by contact date
        user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)
        return render(request, 'accounts/dashboard.html', {'contacts': user_contacts})
    return redirect('login')


MAX_CSV_SIZE = 5 * 1024 * 1024  # 5 MB per file


def admin_panel(request):
    """Website-blended admin area: dashboard stats + CSV bulk upload."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the admin panel.')
        return redirect('index')

    if request.method == 'POST':
        files = request.FILES.getlist('csv_files')
        if not files:
            messages.error(request, 'Please choose at least one CSV file to upload.')
            return redirect('admin_panel')

        realtor_id = request.POST.get('default_realtor')
        default_realtor = None
        if realtor_id:
            default_realtor = Realtor.objects.filter(id=realtor_id).first()

        total_created = total_updated = total_failed = files_done = 0

        for uploaded_file in files:
            if uploaded_file.size > MAX_CSV_SIZE:
                messages.error(request, f'{uploaded_file.name}: skipped — file is larger than 5 MB.')
                continue
            if not uploaded_file.name.lower().endswith('.csv'):
                messages.error(request, f'{uploaded_file.name}: skipped — only .csv files are supported.')
                continue

            stats = parse_listing_csv(uploaded_file, default_realtor=default_realtor)
            CsvImport.objects.create(
                file=uploaded_file,
                original_filename=stats['filename'],
                rows_created=stats['created'],
                rows_updated=stats['updated'],
                rows_failed=stats['failed'],
                errors='\n'.join(stats['errors']),
                uploaded_by=request.user,
            )

            files_done += 1
            total_created += stats['created']
            total_updated += stats['updated']
            total_failed += stats['failed']

            summary = f"{stats['filename']}: {stats['created']} created, {stats['updated']} updated, {stats['failed']} failed"
            if stats['errors']:
                messages.warning(request, summary + ' — see the import log below for row errors.')
            else:
                messages.success(request, summary)

        if files_done:
            messages.success(
                request,
                f'Import finished — {files_done} file(s): {total_created} listings created, '
                f'{total_updated} updated, {total_failed} rows skipped.'
            )

        return redirect('admin_panel')

    context = {
        'stats': {
            'listings': Listing.objects.count(),
            'published': Listing.objects.filter(is_published=True).count(),
            'realtors': Realtor.objects.count(),
            'users': User.objects.count(),
            'reviews': Review.objects.count(),
            'imports': CsvImport.objects.count(),
        },
        'realtors': Realtor.objects.order_by('name'),
        'recent_imports': CsvImport.objects.order_by('-created_at')[:10],
    }
    return render(request, 'accounts/admin_panel.html', context)


def sample_csv(request):
    """Downloadable CSV template showing every supported column."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('index')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="listings_sample.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'title', 'address', 'city', 'state', 'zipcode', 'price',
        'bedrooms', 'bathrooms', 'garage', 'sqft', 'lot_size',
        'description', 'realtor', 'is_published',
    ])
    writer.writerow([
        'Modern Family Home', '456 Oak Avenue', 'Boston', 'MA', '02115',
        '750000', '4', '2.5', '2', '2400', '6000',
        'Beautiful modern home with a large backyard.', 'Jenny Wilson', 'true',
    ])
    writer.writerow([
        'Downtown Loft', '789 Main Street', 'Chicago', 'IL', '60601',
        '$520,000', '2', '1', '1', '1100', '1500',
        'Renovated loft in the heart of downtown.', '', '1',
    ])
    return response
