from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .models import Product


def recent_orders_view(request):
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

    users_with_recent_orders = User.objects.annotate(
        recent_order_count=Count('order', filter=Q(order__created_at__gte=thirty_days_ago))
    ).filter(recent_order_count__gt=0)

    return render(request, 'shop/recent_orders.html', {'users': users_with_recent_orders})


def product_list_view(request):
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    date_filter = request.GET.get('date_filter', '')
    sort = request.GET.get('sort', 'popular')
    page_number = request.GET.get('page', 1)

    products = Product.objects.annotate(
        order_count=Count('orderitem')
    )

    if category:
        products = products.filter(category__iexact=category)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if date_filter == '7':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7))
    elif date_filter == '30':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30))
    elif date_filter == '90':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=90))

    sort_options = {
        'popular': '-order_count',
        'price_asc': 'price',
        'price_desc': '-price',
        'date_asc': 'created_at',
        'date_desc': '-created_at',
    }

    products = products.order_by(sort_options.get(sort, '-order_count'))

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page_number)

    categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'selected_date_filter': date_filter,
        'selected_sort': sort,
    }
    return render(request, 'shop/product_list.html', context)


def ajax_product_list_view(request):
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    date_filter = request.GET.get('date_filter', '')
    sort = request.GET.get('sort', 'popular')
    page_number = request.GET.get('page', 1)

    products = Product.objects.annotate(
        order_count=Count('orderitem')
    )

    if category:
        products = products.filter(category__iexact=category)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if date_filter == '7':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7))
    elif date_filter == '30':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30))
    elif date_filter == '90':
        products = products.filter(created_at__gte=timezone.now() - timezone.timedelta(days=90))

    sort_options = {
        'popular': '-order_count',
        'price_asc': 'price',
        'price_desc': '-price',
        'date_asc': 'created_at',
        'date_desc': '-created_at',
    }

    products = products.order_by(sort_options.get(sort, '-order_count'))

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page_number)

    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': str(product.price),
                'created_at': product.created_at.strftime('%d.%m.%Y'),
                'order_count': product.order_count,
            }
            for product in page_obj
        ],
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'current_page': page_obj.number,
        'num_pages': page_obj.paginator.num_pages,
    }

    return JsonResponse(data)