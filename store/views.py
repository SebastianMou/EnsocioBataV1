from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token

import stripe
from django.conf import settings
from django.http import JsonResponse

from .forms import (UserSellerRegisterForm, UserBuyerRegisterForm, PostForm, 
                    UserUpdateForm, ProfileUpdateForm, UpdatePostForm, CommentForm, ReplyForm)
from .models import Post, Category, Profile, Comment

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
    ng = "http://127.0.0.1:8000/"
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'mxn',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.title,
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=ng + '/checkout_success',
            cancel_url=ng + '/checkout_cancel',
        )
        return redirect(checkout_session.url)
    else:
        return JsonResponse({'error': 'Invalid request method'})

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
    post_count = Post.objects.count()
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)  # If the switch is True, that means Django had to create a new Profile object for the user because it couldn't find an existing one
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'not loged-in')
            return redirect('profile')
    else: 
        u_form = UserUpdateForm(instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'posts': posts,
        'post_count': post_count,
    }
    return render(request, 'autho/profile.html', context)

def visible_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    post_count = Post.objects.filter(author=user).count()
    context = {
        'user': user,
        'posts': posts,
        'post_count': post_count,
    }
    return render(request, 'autho/visible_profile.html', context)

