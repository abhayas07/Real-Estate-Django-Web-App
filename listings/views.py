from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # Correct imports
from .choices import price_choices, bedroom_choices, state_choices
from .models import Listing

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
    # Fetch a specific listing by its ID or return a 404 error if not found
    listing = get_object_or_404(Listing, pk=listing_id)

    context = {
        'listing': listing
    }

    return render(request, 'listings/listing.html', context)

def search(request):
    queryset_list = Listing.objects.order_by('-list_date')

    # Keywords filter
    keywords = request.GET.get('keywords')

    if keywords:
        # queryset_list = queryset_list.filter(description__icontains=keywords)
        queryset_list = queryset_list.filter(title__icontains=keywords)
        
  

    # if keywords:
    #     queryset_list = queryset_list.filter(description__icontains=keywords)
    #     queryset_list = queryset_list.filter(description__icontains=keywords) 
    # City filter
    city = request.GET.get('city')
    if city:
        queryset_list = queryset_list.filter(city__iexact=city)

    # State filter
    state = request.GET.get('state')
    if state:
        queryset_list = queryset_list.filter(state__iexact=state)

    # Bedrooms filter
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        queryset_list = queryset_list.filter(bedrooms__lte=bedrooms)

    # Price filter
    price = request.GET.get('price')
    if price:
        queryset_list = queryset_list.filter(price__lte=price)

    # Use pagination helper
    paged_listings = paginate_listings(request, queryset_list)

    context = {
        'state_choices': state_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices,
        'listings': paged_listings,
        'values': request.GET
    }

    return render(request, 'listings/search.html', context)
