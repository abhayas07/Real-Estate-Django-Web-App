"""Verify CSV upload works directly inside the Django admin site."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.test import Client  # noqa: E402

from listings.models import Listing, CsvImport  # noqa: E402

User.objects.filter(username='admincsvcheck').delete()
admin = User.objects.create_user(
    username='admincsvcheck', password='AdminCheck!1', is_staff=True, is_superuser=True)

csv_content = (
    'title,city,state,zipcode,price,bedrooms,bathrooms,sqft,lot_size,description\n'
    'Admin CSV Bungalow,Adminville,AV,88888,399000,3,2,1500,4000,Uploaded from the admin site\n'
).encode('utf-8')

client = Client()
client.force_login(admin)

r = client.get('/admin/listings/csvimport/')
print('admin changelist ->', r.status_code, '(expect 200)')

before = Listing.objects.count()
r = client.post('/admin/listings/csvimport/add/', {
    'file': SimpleUploadedFile('admin_batch.csv', csv_content, content_type='text/csv'),
}, follow=True)
print('admin upload add ->', r.status_code, '(expect 200 after redirect to changelist)')

record = CsvImport.objects.filter(original_filename='admin_batch.csv').first()
print('import record created:', record is not None)
if record:
    print('  rows created:', record.rows_created, '(expect 1)')
    print('  uploaded_by:', record.uploaded_by)
listing = Listing.objects.filter(title__iexact='Admin CSV Bungalow').first()
print('listing created in admin:', listing is not None, '| total delta:', Listing.objects.count() - before)
if listing:
    print('  has photo:', bool(listing.photo_main), '| realtor:', listing.realtor)

# cleanup
if record:
    record.file.delete(save=False)
    record.delete()
if listing:
    listing.delete()
admin.delete()
print('cleanup done')
