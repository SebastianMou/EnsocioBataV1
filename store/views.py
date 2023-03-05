from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token

from .forms import (UserSellerRegisterForm, UserBuyerRegisterForm, PostForm, 
                    UserUpdateForm, ProfileUpdateForm, UpdatePostForm)
from .models import Post, Category, Profile

# Create your views here.
def home(request):
    categories = Category.objects.filter(
        Q(name__startswith='Vídeo y animación') | Q(name__startswith='Diseño gráfico') |
        Q(name__startswith='Publicidad digital')
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
            return redirect('/')
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
        return redirect('/')
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
                messages.error(request, 'This email is already registered.')
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
                return redirect('/')
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
    post.delete()
    return redirect('/')

def all_posts(request):
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'service/all_posts.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    context = {
        'post': post,
    }
    return render(request, 'service/post_detail.html', context)

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
    }
    return render(request, 'autho/profile.html', context)

