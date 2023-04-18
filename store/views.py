from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

from .forms import (UserSellerRegisterForm, UserBuyerRegisterForm, PostForm, 
                    UserUpdateForm, ProfileUpdateForm, UpdatePostForm, CommentForm, ReplyForm)
from .models import Post, Category, Profile, Comment, CartItem, Message, Transaction

import stripe
import logging
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        subject = request.POST.get('subject')
        name = request.POST.get('name')
        data = {
            'complaint': 'ENSOCIO.MX',
            'name': name,
            'subject': subject,
            'email': email,
            'message': message, 
        }
        message = '''
        From: {}
        Email: {}
        New message: {}
        '''.format(data['name'], data['email'], data['message'])
        send_mail(data['complaint'], message, '', ['ensocio.mx@gmail.com'])

    categories = Category.objects.filter(
        Q(name__startswith='Servicios de voz') | Q(name__startswith='Diseño gráfico') |
        Q(name__startswith='Servicios de SEO')
    )[:3]
    context = {
        'categories': categories,
    }
    return render(request, 'home.html', context)

def category_list(request, pk):
    if request.method == 'POST':
        query = request.POST.get('search')
        results = Post.objects.filter(title__icontains=query)

        categories = Category.objects.all()
        category = get_object_or_404(Category, pk=pk)
        posts = Post.objects.filter(category=category)
        context = {
            'categories': categories,
            'category': category,
            'posts': posts,
            'results': results,
        }
        return render(request, 'service/category.html', context)
    else:
        categories = Category.objects.all()
        category = get_object_or_404(Category, pk=pk)
        posts = Post.objects.filter(category=category)
        context = {
            'categories': categories,
            'category': category,
            'posts': posts,
        }
        return render(request, 'service/category.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'contraseña o nombre de usuario incorrecto')
            return redirect('user_login')
    else:
        pass
    return render(request, 'autho/user_login.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'autho/delete_account.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('user_login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return render(request, 'home.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('authentication/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

def seller_register(request):
    if request.method == 'POST':
        form = UserSellerRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return redirect('seller_register')
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail(request, user, form.cleaned_data.get('email'))
                return redirect('/')
    else:
        form = UserSellerRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'autho/seller_register.html', context)


def activate_buyer(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('user_login')
    else:
        messages.error(request, 'Activation link is invalid!')
    return render(request, 'home.html')

def activateEmail_buyer(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('authentication/template_activate_account_buyer.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

def buyer_register(request):
    if request.method == 'POST':
        form = UserBuyerRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este correo electrónico ya está registrado.')
                return redirect('buyer_register')
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail_buyer(request, user, form.cleaned_data.get('email'))
                return redirect('/')
    else:
        form = UserBuyerRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'autho/buyer_register.html', context)

@csrf_protect
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if hasattr(request.user, 'account') and request.user.account.freelancer_key:
                post.author = request.user
                post.save()
                return redirect('post_detail', pk=post.pk)
            else:
                form.add_error(None, 'You must have a freelancer key number to create a post.')
    else:
        form = PostForm()
    return render(request, 'service/create_posts.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.author != request.user:
        return redirect('/')

    if request.method == 'POST':
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post_detail', args=[post.pk]))
    else:
        form = UpdatePostForm(instance=post)
    context = {
        'form': form,
    }
    return render(request, 'service/edit_post.html', context)

@login_required
def delete(request, post_id=None):
    post = Post.objects.get(id=post_id)
    if post.author != request.user:
        return redirect('/')
    post.delete()
    return redirect('profile')

def all_posts(request):
    posts = Post.objects.all()
    categories = Category.objects.all()
    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'service/all_posts.html', context)

def post_detail(request, pk):
    product = get_object_or_404(Post, pk=pk)
    comments = product.comment_set.filter(parent__isnull=True)
    cout_reviews = Comment.objects.filter(product=product).count()
    # current_url = request.build_absolute_uri()
    related_products = product.related_products()

    if request.user.is_authenticated:
        is_favorite = product.cartitem_set.filter(user=request.user).exists()
    else:
        is_favorite = None

    if request.method == 'POST':
        form = CommentForm(request.POST)
        reply_form = ReplyForm(request.POST)
        if 'comment_id' in request.POST:  # processing a reply
            comment = get_object_or_404(Comment, pk=request.POST['comment_id'])
            reply = reply_form.save(commit=False)
            reply.product = product
            reply.author = request.user
            reply.parent = comment
            reply.save()
            return redirect('post_detail', pk=pk)  # redirect back to the same page after replying
        elif form.is_valid():  # processing a new top-level comment
            comment = form.save(commit=False)
            comment.product = product
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=pk)  # redirect back to the same page after commenting
    else:
        form = CommentForm()
        reply_form = ReplyForm()
    context = {
        'product': product,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'comments': comments,
        'form': form,
        'reply_form': reply_form,
        'cout_reviews': cout_reviews,
        'is_favorite': is_favorite,
        # 'current_url': current_url,
        'related_products': related_products,
    }
    return render(request, 'service/post_detail.html', context)

def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'Unable to delete comment.')
    return redirect('post_detail', pk=comment.product.pk)

def create_checkout_session(request, pk):
    product = get_object_or_404(Post, pk=pk)
    ng = "https://ensocio.herokuapp.com/"
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        quantity = int(request.POST.get('quantity', 1))
        name = f"{product.author} - {product.title}"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'mxn',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': name,
                            'description': product.category,
                        },
                    },
                    'quantity': quantity,
                },
            ],
            mode='payment',
            success_url=ng + '/checkout_success',
            cancel_url=ng + '/checkout_cancel',
            metadata={
                'post_id': product.id,
                'seller_id': product.author.id,
                'buyer_id': request.user.id,
                'quantity': quantity,
            },
        )
        return redirect(checkout_session.url)
    else:
        return JsonResponse({'error': 'Invalid request method'})

def post_like(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        post.dislikes.remove(request.user)
    return redirect('post_detail', pk=post.id)

def post_dislike(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
        post.likes.remove(request.user)
    return redirect('post_detail', pk=post.id)

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    if "HTTP_STRIPE_SIGNATURE" not in request.META:
        logger.error(f"Missing Stripe signature. Headers: {request.META}")
        return HttpResponseBadRequest("Missing Stripe signature")

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        post_id = session['metadata']['post_id']
        seller_id = session['metadata']['seller_id']
        buyer_id = session['metadata']['buyer_id']
        quantity = session['metadata']['quantity']

        post = Post.objects.get(id=post_id)
        seller = User.objects.get(id=seller_id)
        buyer = User.objects.get(id=buyer_id)

        transaction = Transaction(
            buyer=buyer,
            seller=seller,
            post=post,
            quantity=quantity,
            amount=session['amount_total']
        )
        transaction.save()
        logger.info(f"Transaction saved: {transaction}")

    else:
        logger.warning(f"Received an unhandled event: {event}")

    return HttpResponse(status=200)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/list.html', {'transactions': transactions})

def checkout_success(request):
    return render(request, 'checkout_success.html')

def checkout_cancel(request):
    return render(request, 'checkout_cancel.html')

def search(request):
    if request.method == 'POST':
        query = request.POST.get('search')
        results = Post.objects.filter(title__icontains=query)
        results_c = Category.objects.filter(name__icontains=query)
        context = {
            'results': results,
            'query': query,
            'results_c': results_c,
        }
        return render(request, 'service/search.html', context)
    else:
        return render(request, 'service/search.html') 

@login_required
def profile(request):
    posts = Post.objects.filter(author=request.user)

    favorite_posts = CartItem.objects.filter(user=request.user).values_list('post', flat=True)
    cart_items = Post.objects.filter(id__in=favorite_posts)
    post_count = Post.objects.filter(author=request.user).count()
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)  # If the switch is True, that means Django had to create a new Profile object for the user because it couldn't find an existing one
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'not loged-in')
            # get all comments on user's posts
            comments = Comment.objects.filter(product__author=request.user)
            # comments_reply_post = Comment.objects.filter(Q(product__author=request.user) | Q(parent__product__author=request.user)).select_related('author', 'parent__author')
            comments_reply_post = Comment.objects.filter(parent__product__author=request.user)
            
            context = {
                'u_form': u_form,
                'p_form': p_form,
                'posts': posts,
                'post_count': post_count,
                'cart_items': cart_items,
                'comments': comments,
                'comments_reply_post': comments_reply_post,
            }
            return render(request, 'autho/profile.html', context)
    else: 
        u_form = UserUpdateForm(instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    comments = Comment.objects.filter(product__author=request.user)
    # comments_reply_post = Comment.objects.filter(Q(product__author=request.user) | Q(parent__product__author=request.user)).select_related('author', 'parent__author')
    comments_reply_post = Comment.objects.filter(parent__author=request.user)
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'posts': posts,
        'post_count': post_count,
        'cart_items': cart_items,
        'comments': comments,
        'comments_reply_post': comments_reply_post,
    }
    return render(request, 'autho/profile.html', context)

def favorite_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    favorite, created = CartItem.objects.get_or_create(user=request.user, post=post)
    if not created:
        favorite.delete()
    return redirect('post_detail', pk=post.pk)

def visible_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    post_count = Post.objects.filter(author=user).count()
    last_login = user.last_login
    current_time = timezone.now()
    if request.user == user:
        show_chat_button = False
    else:
        show_chat_button = True
    if current_time - last_login < timezone.timedelta(minutes=5):
        is_active = True
    else:
        is_active = False
    context = {
        'user': user,
        'posts': posts,
        'post_count': post_count,
        'is_active': is_active,
        'show_chat_button': show_chat_button,
    }
    return render(request, 'autho/visible_profile.html', context)

@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {
        'directs': directs,
        'active_direct': active_direct,
        'messages': messages,
    }
    return render(request, 'autho/inbox.html', context)

@login_required
def directs(request, username):
    sending_message_to = get_object_or_404(User, username=username)
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)
    directs.update(is_read=True)
    
    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    context = {
        'sending_message_to': sending_message_to,
        'directs': directs,
        'active_direct': active_direct,
        'messages': messages,
    }
    return render(request, 'autho/directs.html', context)

def send_message_ajax(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to_user')
        body = request.POST.get('body')
        file = request.FILES.get('file')

        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body, file)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'})

def get_messages_ajax(request, username):
    user = request.user
    sending_message_to = get_object_or_404(User, username=username)
    directs = Message.objects.filter(user=user, reciepient__username=username)
    directs.update(is_read=True)

    messages = []
    for direct in directs:
        message_data = {
            'sender': direct.sender.username,
            'body': direct.body,
            'date': direct.date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if direct.file:
            message_data['file_url'] = direct.file.url
        messages.append(message_data)

    # print(messages)  # Add this line to print messages data
    return JsonResponse({'messages': messages})
