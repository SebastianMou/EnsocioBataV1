from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from PIL import Image

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    freelancer_key = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = 'accounts'

    def __str__(self) -> str:
        return self.user.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(default='Hi my name is ... ', max_length=355)
    user_image = models.ImageField(upload_to='media', validators=[FileExtensionValidator(['png', 'jpg'])], default='default.png')

    def __str__(self) -> str:
        return f'profile of -> {self.user.username}'
    
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.user_image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.user_image.path)

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    category_image = models.ImageField(upload_to='cIcons/', null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Post(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=1599)
    detailed_description = RichTextField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    image2 = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    image3 = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    price = models.IntegerField(default=0, null=True)
    is_active = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    favorite = models.ManyToManyField(User, related_name='favorites', blank=True)

    class Meta:
        verbose_name_plural = 'Posts'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)

class Comment(models.Model):
    product = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return str(self.parent) + ' -> ' + str(self.author) + ' -> ' + str(self.text)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
