from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.forms.widgets import ClearableFileInput

from .models import Account, Category, Post, Profile

class UserSellerRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'First Name',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Last Name',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Username',
    }))
    freelancer_key = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Phone Number',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'password1',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'password1',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'freelancer_key']
    
    def clean_freelancer_key(self):
        freelancer_key = self.cleaned_data.get('freelancer_key')
        if Account.objects.filter(freelancer_key=freelancer_key).exists():
            raise ValidationError('This phone number is already registered.')
        return freelancer_key

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        account = Account(user=user, freelancer_key=self.cleaned_data['freelancer_key'])
        account.save()
        return user
    
class UserBuyerRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'First Name',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Last Name',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Username',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Email'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'password1',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'password1',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    detailed_description = RichTextField()
    image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image2 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image3 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    price = forms.DecimalField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter price here (e.g. 10.99)',
    }))
    is_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }), required=True)

    class Meta:
        model = Post
        fields = ['category', 'title', 'content', 'detailed_description', 'image', 'image2', 'image3', 'price', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title here',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter content here',
                'rows': 10,
            }),
        }

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'First Name',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Last Name',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Username',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'email'
    }))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    user_image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'bio',
        'rows': 5,
        'cols': 40,
    }))
    class Meta:
        model = Profile
        fields = ['user_image', 'bio']

class UpdatePostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'title',
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'content',
        'rows': 5,
        'cols': 40,
    }))
    detailed_description = RichTextField()
    price = forms.DecimalField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Price',
    }))
    is_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input custom-control-input',
        'id': 'customSwitch2',
    }))
    image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image2 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image3 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    class Meta:
        model = Post
        fields = [
            'category', 'title', 'content', 'detailed_description', 
            'image', 'image2', 'image3', 'price', 'is_active',
        ]