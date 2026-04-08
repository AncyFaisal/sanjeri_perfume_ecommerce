# views/homepage.py
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Product, ProductVariant, Cart, CartItem, Wishlist, WishlistItem

def homepage(request):
    """Home page view with actual products and search functionality"""
    query = request.GET.get('q', '')
    
    # Get all active variants
    all_variants = ProductVariant.objects.filter(
        is_active=True,
        product__is_active=True,
        product__is_deleted=False
    ).select_related('product')
    
    cart_item_count = 0
    wishlist_product_ids = []
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = cart.total_items
        except Cart.DoesNotExist:
            pass
        
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_product_ids = list(WishlistItem.objects.filter(
                wishlist=wishlist
            ).values_list('product_id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    # Apply search filter if query exists
    if query:
        search_variants = all_variants.filter(
            Q(product__name__icontains=query) | 
            Q(product__brand__icontains=query) |
            Q(product__description__icontains=query) |
            Q(product__fragrance_type__icontains=query) |
            Q(sku__icontains=query)
        )
        is_searching = True
        search_results_count = search_variants.values('product_id').distinct().count()
    else:
        search_variants = None
        is_searching = False
        search_results_count = 0

    # Get featured products (only show if not searching)
    if not is_searching:
        # We need a way to distinct on product while ordering, but MySQL doesn't support distinct(field).
        # We'll just take the top 8 variants from featured products. Alternatively, filter featured.
        featured_variants = all_variants.filter(product__is_featured=True)[:8]
    else:
        featured_variants = search_variants[:8] if search_variants else []
    
    # Get variants by gender for different sections. 
    # Just grab 4 variants of each category.
    mens_variants = all_variants.filter(gender="Male")[:4]
    womens_variants = all_variants.filter(gender="Female")[:4]
    unisex_variants = all_variants.filter(gender="Unisex")[:4]

    # Add is_in_wishlist attribute to each variant's product
    for variant in featured_variants:
        variant.product.is_in_wishlist = variant.product.id in wishlist_product_ids
    
    for variant in mens_variants:
        variant.product.is_in_wishlist = variant.product.id in wishlist_product_ids
    
    for variant in womens_variants:
        variant.product.is_in_wishlist = variant.product.id in wishlist_product_ids
    
    for variant in unisex_variants:
        variant.product.is_in_wishlist = variant.product.id in wishlist_product_ids

    context = {
        'title': 'Home - Sanjeri',
        'featured_products': featured_variants,
        'mens_products': mens_variants,
        'womens_products': womens_variants,
        'unisex_products': unisex_variants,
        'user': request.user,
        'search_query': query,
        'is_searching': is_searching,
        'search_results_count': search_results_count,
        'search_products': search_variants,
        'cart_item_count': cart_item_count,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'homepage.html', context)

