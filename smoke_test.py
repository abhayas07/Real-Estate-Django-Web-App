"""Smoke test the whole site through Django's test client."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.test import Client  # noqa: E402

client = Client()

urls = [
    '/',
    '/about',
    '/listings/',
    '/listings/search',
    '/accounts/login/',
    '/accounts/register/',
    '/realtors/login/',
    '/realtors/register/',
    '/realtors/forgot-password/',
    '/accounts/dashboard/',
    '/contacts/contact',
    '/this-page-does-not-exist',
]

print('--- Anonymous page smoke test ---')
for u in urls:
    try:
        r = client.get(u, follow=True)
        print(f'{u} -> {r.status_code}')
    except Exception as e:
        print(f'{u} -> EXCEPTION: {type(e).__name__}: {e}')

print('--- Listing detail pages ---')
from listings.models import Listing  # noqa: E402

for l in Listing.objects.all()[:5]:
    try:
        r1 = client.get(f'/listings/{l.id}')
        r2 = client.get(f'/listings/listing/{l.id}/')
        print(f'listing {l.id} -> detail {r1.status_code}, reviews {r2.status_code}')
    except Exception as e:
        print(f'listing {l.id} -> EXCEPTION: {type(e).__name__}: {e}')

print('--- Register / login / logout flow ---')
import time  # noqa: E402

username = 'smoketest{}'.format(int(time.time()))

# Password mismatch
r = client.post('/accounts/register/', {
    'username': username, 'email': f'{username}@test.com',
    'password': 'Sup3rSecret!', 'password2': 'different',
}, follow=True)
print('register mismatch ->', r.status_code, '(should redirect back to register)')

# Valid registration
r = client.post('/accounts/register/', {
    'first_name': 'Smoke', 'last_name': 'Tester',
    'username': username, 'email': f'{username}@test.com',
    'password': 'Sup3rSecret!42', 'password2': 'Sup3rSecret!42',
}, follow=True)
print('register valid ->', r.status_code, '(expect 200 after redirect to dashboard)')

# Dashboard as authenticated user
r = client.get('/accounts/dashboard/')
print('dashboard ->', r.status_code, '(expect 200)')

# Weak password rejected
r = client.post('/accounts/register/', {
    'username': username + 'x', 'email': 'weak@test.com',
    'password': '123', 'password2': '123',
}, follow=True)
print('register weak pw ->', r.status_code, '(should bounce back to register)')

# Logout
r = client.post('/accounts/logout/', follow=True)
print('logout ->', r.status_code)

# Login again
r = client.post('/accounts/login/', {'username': username, 'password': 'Sup3rSecret!42'}, follow=True)
print('login ->', r.status_code, '(expect 200 after redirect to dashboard)')

print('--- Search filters ---')
r = client.get('/listings/search?keywords=pool&state=CA&bedrooms=3&price=500000')
print('search w/ filters ->', r.status_code)
r = client.get('/listings/search?page=1&keywords=nothingmatchesxyz')
print('search no results ->', r.status_code)
