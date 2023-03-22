from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.forms.widgets import ClearableFileInput

from .models import Account, Category, Post, Profile, Comment

class UserSellerRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Apellido',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre de usuario',
    }))
    freelancer_key = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Clave de freelancer',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Correo electrónico'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar contraseña',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'freelancer_key']
    
    def clean_freelancer_key(self):
        freelancer_key = self.cleaned_data.get('freelancer_key')
        if Account.objects.filter(freelancer_key=freelancer_key).exists():
            raise ValidationError('Esta clave de identificación ya está registrada.')
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
        'placeholder': 'contraseña',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar contraseña',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('','Buscar categoría escribiendo')] + list(self.fields['category'].choices)[1:]

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
        'placeholder': 'Introduce el precio aquí (por ejemplo, 10.99)',
    }))
    is_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
        'style': 'width: 22px; height: 22px;',
    }), required=True)

    class Meta:
        model = Post
        fields = ['category', 'title', 'content', 'detailed_description', 'image', 'image2', 'image3', 'price', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título aquí',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explica brevemente sobre ti y que haces',
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
    }), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('','Buscar categoría escribiendo')] + list(self.fields['category'].choices)[1:]

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
        'placeholder': 'Introduce el precio aquí (por ejemplo, 10.99)',
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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your review here...',
                'rows': 4,
                'cols': 50
            }),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'id': 'reply-input',
                'placeholder': 'Enter your review here...',
                'rows': 1,
            }),
        }