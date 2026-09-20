from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import (
    Category,
    Product,
    CartItem,
    Wishlist,
    Order,
    Review,
    OrderItem,
)


def home(request):

    categories = Category.objects.all()

    products = Product.objects.filter(
        is_available=True
    )[:8]

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:

        cart_count = sum(
            item.quantity
            for item in CartItem.objects.filter(
                user=request.user
            )
        )

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    context = {
        'categories': categories,
        'products': products,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }

    return render(
        request,
        'store/home.html',
        context
    )

def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    product = Product.objects.get(id=product_id)

    if product.stock <= 0:
       messages.error(request, 'This product is currently out of stock.')
       return redirect('shop')
    product = Product.objects.get(id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1

    cart_item.save()

    return redirect('home')

def cart(request):

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    cart_items = CartItem.objects.filter(user=request.user)

    total = sum(item.total_price() for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'store/cart.html', context)

def increase_quantity(request, item_id):

    if not request.user.is_authenticated:
        return redirect('login')

    item = CartItem.objects.get(
        id=item_id,
        user=request.user
    )

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('cart')


def decrease_quantity(request, item_id):

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    item = CartItem.objects.get(
        id=item_id,
        user=request.user
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()

    return redirect('cart')

def remove_from_cart(request, item_id):

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    item = CartItem.objects.get(
        id=item_id,
        user=request.user
    )

    item.delete()

    return redirect('cart')

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(request, 'store/register.html')

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')

def logout_view(request):

    logout(request)

    return redirect('home')

def add_to_wishlist(request, product_id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('home')

def wishlist(request):

    if not request.user.is_authenticated:
        return redirect('login')

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        'store/wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


def remove_from_wishlist(request, item_id):

    if not request.user.is_authenticated:
        return redirect('login')

    item = Wishlist.objects.get(
        id=item_id,
        user=request.user
    )

    item.delete()

    return redirect('wishlist')

def product_detail(request, product_id):

    product = Product.objects.get(id=product_id)

    # Product reviews
    reviews = product.reviews.all()

    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(
        id=product.id
    )[:4]

    # Reviews rating
    total_reviews = reviews.count()

    if total_reviews > 0:
        average_rating = sum(
            review.rating for review in reviews
        ) / total_reviews
    else:
        average_rating = 0

    # Cart & wishlist counts
    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:

        cart_count = sum(
            item.quantity
            for item in CartItem.objects.filter(
                user=request.user
            )
        )

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    return render(
        request,
        'store/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'total_reviews': total_reviews,
            'average_rating': average_rating,
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
            'related_products': related_products,
        }
    )

def checkout(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = CartItem.objects.filter(
        user=request.user
    )

    total = sum(
        item.total_price()
        for item in cart_items
    )

    if not cart_items.exists():
        return redirect('cart')

    if request.method == 'POST':

        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            address=address,
            phone=phone
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        return redirect('order_success', order_id=order.id)

    return render(
        request,
        'store/checkout.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )

def order_success(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'store/order_success.html',
        {
            'order': order
        }
    )

def my_orders(request):

    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/my_orders.html',
        {
            'orders': orders
        }
    )

def order_detail(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'store/order_detail.html',
        {
            'order': order
        }
    )

def shop(request):

    products = Product.objects.filter(
        is_available=True
    ).order_by('-created_at')

    categories = Category.objects.all()

    search = request.GET.get('search')
    category_id = request.GET.get('category')

    if search:
        products = products.filter(
            name__icontains=search
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:

        cart_count = sum(
            item.quantity
            for item in CartItem.objects.filter(
                user=request.user
            )
        )

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    return render(
        request,
        'store/shop.html',
        {
            'products': products,
            'categories': categories,
            'search': search,
            'selected_category': category_id,
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
        }
    )

def cancel_order(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()

    return redirect('order_detail', order_id=order.id)

def add_review(request, product_id):

    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)

    if request.method == 'POST':

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:

            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )

        return redirect(
            'product_detail',
            product_id=product.id
        )

    return redirect(
        'product_detail',
        product_id=product.id
    )  

def about(request):
    return render(request, 'store/about.html')      

def contact(request):
    return render(request, 'store/contact.html')   

def faq(request):
    return render(request, 'store/faq.html')

def offers(request):
    return render(request, 'store/offers.html')

def categories(request):
    return render(request, 'store/categories.html')

def shipping(request):
    return render(request, 'store/shipping.html')

def returns(request):
    return render(request, 'store/returns.html')

