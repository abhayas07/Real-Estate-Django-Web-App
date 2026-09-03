"""
CSV bulk import for listings.

Used by both the website admin panel (multiple files at once) and the
Django admin (single file per upload record).
"""
import csv
import io
import os
import shutil

from django.conf import settings
from django.core.files import File

from .models import Listing
from realtors.models import Realtor

# Flexible header names -> model field
COLUMN_ALIASES = {
    'title': 'title', 'name': 'title', 'property': 'title',
    'address': 'address', 'street': 'address', 'street_address': 'address',
    'city': 'city',
    'state': 'state',
    'zipcode': 'zipcode', 'zip': 'zipcode', 'zip_code': 'zipcode', 'postal_code': 'zipcode',
    'price': 'price', 'asking_price': 'price',
    'bedrooms': 'bedrooms', 'beds': 'bedrooms',
    'bathrooms': 'bathrooms', 'baths': 'bathrooms',
    'garage': 'garage',
    'sqft': 'sqft', 'sq_ft': 'sqft', 'square_feet': 'sqft',
    'lot_size': 'lot_size', 'lotsize': 'lot_size', 'lot': 'lot_size',
    'description': 'description', 'details': 'description',
    'realtor': 'realtor', 'agent': 'realtor',
    'is_published': 'is_published', 'published': 'is_published',
}


def _norm_header(header):
    return header.strip().lower().replace(' ', '_').replace('-', '_')


def _parse_int(value, default):
    if not value:
        return default
    cleaned = value.replace('$', '').replace(',', '').strip()
    return int(float(cleaned))


def _parse_decimal(value, default):
    if not value:
        return default
    cleaned = value.replace('$', '').replace(',', '').strip()
    number = float(cleaned)
    if number > 9999.9:
        raise ValueError('value too large (max 9999.9)')
    return round(number, 1)


def _parse_bool(value, default):
    if not value:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'y', 'published')


def _resolve_realtor(name, default_realtor):
    if name:
        realtor = Realtor.objects.filter(name__iexact=name).first()
        if realtor is None:
            realtor = Realtor.objects.filter(email__iexact=name).first()
        if realtor is not None:
            return realtor
    if default_realtor is not None:
        return default_realtor
    return Realtor.objects.first()


def _ensure_placeholder_photo():
    """Return a path to a reusable placeholder photo for CSV listings."""
    target = os.path.join(str(settings.MEDIA_ROOT), 'photos', 'placeholder.jpg')
    if not os.path.exists(target):
        candidates = [
            os.path.join(str(settings.BASE_DIR), 'static', 'img', 'homes', 'home-1.jpg'),
            os.path.join(str(settings.BASE_DIR), 'realestate', 'static', 'img', 'homes', 'home-1.jpg'),
        ]
        for src in candidates:
            if os.path.exists(src):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(src, target)
                break
    return target


def parse_listing_csv(file_obj, default_realtor=None):
    """Parse one CSV file and import its rows as Listing records.

    Returns a dict: filename, created, updated, failed, errors[].
    Does NOT create the CsvImport audit record — callers do that so the
    uploaded file is stored exactly once.
    """
    stats = {
        'filename': getattr(file_obj, 'name', 'upload.csv'),
        'created': 0,
        'updated': 0,
        'failed': 0,
        'errors': [],
    }

    filename = getattr(file_obj, 'name', '')
    if not filename.lower().endswith('.csv'):
        stats['failed'] = 1
        stats['errors'].append('Skipped: only .csv files are supported.')
        return stats

    raw = file_obj.read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            text = raw.decode('latin-1')
        except UnicodeDecodeError:
            stats['failed'] = 1
            stats['errors'].append('Could not decode the file as text (expected UTF-8 CSV).')
            return stats

    # Detect delimiter (comma, semicolon or tab)
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel  # default comma

    rows = list(csv.reader(io.StringIO(text), dialect))
    if len(rows) < 2:
        stats['failed'] = 1
        stats['errors'].append('File has no data rows.')
        return stats

    # Map header columns (flexible aliases, case-insensitive)
    mapping = {}
    for idx, header in enumerate(rows[0]):
        key = COLUMN_ALIASES.get(_norm_header(header))
        if key:
            mapping[key] = idx

    missing_columns = [col for col in ('title', 'price') if col not in mapping]
    if missing_columns:
        stats['failed'] = 1
        stats['errors'].append(
            'Missing required column(s): ' + ', '.join(missing_columns) +
            '. Required: title, price. Optional: address, city, state, zipcode, '
            'bedrooms, bathrooms, garage, sqft, lot_size, description, realtor, is_published.'
        )
        return stats

    placeholder_path = _ensure_placeholder_photo()

    for line_no, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue  # skip blank lines

        try:
            def get(col):
                idx = mapping.get(col)
                if idx is None or idx >= len(row):
                    return ''
                return row[idx].strip()

            title = get('title')
            price_raw = get('price')
            if not title:
                raise ValueError('title is required')
            if not price_raw:
                raise ValueError('price is required')

            price = int(float(price_raw.replace('$', '').replace(',', '').strip()))

            bedrooms = _parse_int(get('bedrooms'), 0)
            bathrooms = _parse_decimal(get('bathrooms'), 0)
            garage = _parse_int(get('garage'), 0)
            sqft = _parse_int(get('sqft'), 0)
            lot_size = _parse_decimal(get('lot_size'), 0)
            if bathrooms > 9.9:
                raise ValueError('bathrooms must be 9.9 or less')
            if lot_size > 9999.9:
                raise ValueError('lot_size must be 9999.9 or less')

            realtor = _resolve_realtor(get('realtor'), default_realtor)
            if realtor is None:
                raise ValueError(
                    "no realtor matched (set the 'realtor' column, choose a default "
                    'realtor in the upload form, or add a realtor in the admin area)'
                )

            fields = {
                'address': get('address'),
                'city': get('city'),
                'state': get('state'),
                'zipcode': get('zipcode'),
                'description': get('description'),
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'garage': garage,
                'sqft': sqft,
                'lot_size': lot_size,
                'is_published': _parse_bool(get('is_published'), True),
            }

            # Update if a listing with the same title + zipcode already exists
            existing = Listing.objects.filter(
                title__iexact=title, zipcode__iexact=fields['zipcode']
            ).first()

            if existing is not None:
                for field, value in fields.items():
                    setattr(existing, field, value)
                existing.realtor = realtor
                existing.save()
                stats['updated'] += 1
            else:
                listing = Listing(
                    title=title,
                    realtor=realtor,
                    **fields,
                )
                with open(placeholder_path, 'rb') as fh:
                    listing.photo_main.save('placeholder.jpg', File(fh), save=False)
                listing.save()
                stats['created'] += 1

        except (ValueError, TypeError) as exc:
            stats['failed'] += 1
            stats['errors'].append(f'Row {line_no}: {exc}')

    return stats