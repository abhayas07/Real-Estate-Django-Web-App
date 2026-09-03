from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Listing, Review
from .choices import price_choices, bedroom_choices, state_choices


def listing_detail(request, listing_id):
    """Reviews page for a listing."""
    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, 'listings/listing_detail.html', {'listing': listing})


@login_required
def add_review(request, listing_id):
    # Fetch the listing or return a 404 error if it doesn't exist
    listing = get_object_or_404(Listing, id=listing_id)

    if request.method == "POST":
        # Get rating and comment from the POST request
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = None

        if rating is None or not 1 <= rating <= 5:
            messages.error(request, 'Please select a rating between 1 and 5.')
            return redirect('add_review', listing_id=listing.id)

        if not comment.strip():
            messages.error(request, 'Please write a short comment for your review.')
            return redirect('add_review', listing_id=listing.id)

        # Create a new review
        Review.objects.create(
            listing=listing,
            user=request.user,
            rating=rating,
            comment=comment
        )

        messages.success(request, 'Thank you! Your review has been posted.')
        # Redirect to the reviews page
        return redirect('listing_detail', listing_id=listing.id)

    # If it's a GET request, render the add review form
    return render(request, 'listings/add_review.html', {'listing': listing})


def paginate_listings(request, queryset):
    """Helper function for pagination."""
    paginator = Paginator(queryset, 6)  # 6 listings per page
    page = request.GET.get('page')  # Get the page number from GET request
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page
        return paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page
        return paginator.page(paginator.num_pages)


def index(request):
    # Fetch the listings, ordered by list_date and filtered for published ones
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)

    # Use pagination helper
    paged_listings = paginate_listings(request, listings)

    context = {
        'listings': paged_listings
    }

    return render(request, 'listings/listings.html', context)


def listing(request, listing_id):
    # Fetch a specific listing by its ID or return a 404 if not found
    listing = get_object_or_404(Listing, pk=listing_id)

    context = {
        'listing': listing
    }

    return render(request, 'listings/listing.html', context)


def search(request):
    queryset_list = Listing.objects.order_by('-list_date')

    # Keywords filter (matches title or description)
    keywords = request.GET.get('keywords')
    if keywords:
        queryset_list = queryset_list.filter(
            Q(title__icontains=keywords) | Q(description__icontains=keywords)
        )

    # City filter
    city = request.GET.get('city')
    if city:
        queryset_list = queryset_list.filter(city__iexact=city)

    # State filter
    state = request.GET.get('state')
    if state:
        queryset_list = queryset_list.filter(state__iexact=state)

    # Bedrooms filter (minimum number of bedrooms)
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        queryset_list = queryset_list.filter(bedrooms__gte=bedrooms)

    # Price filter (maximum price)
    price = request.GET.get('price')
    if price:
        queryset_list = queryset_list.filter(price__lte=price)

    # Use pagination helper
    paged_listings = paginate_listings(request, queryset_list)

    # Preserve the search filters across pagination links
    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'state_choices': state_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices,
        'listings': paged_listings,
        'values': request.GET,
        'params': params.urlencode()
    }

    return render(request, 'listings/search.html', context)
