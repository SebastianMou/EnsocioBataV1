from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.urls import reverse
from django.db.models import Max

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
    is_active = models.BooleanField(default=True)

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
    STATUS_CHOICES = (
        ('1 día', '1 día'),
        ('2 días', '2 días'),
        ('3 días', '3 días'),
        ('4 días', '4 días'),
        ('5 días', '5 días'),
        ('6 días', '6 días'),
        ('1 semana', '1 semana'),
        ('2 semanas', '2 semanas'),
        ('3 semanas', '3 semanas'),
        ('1 mes', '1 mes'),
        ('2 meses', '2 meses'),
    )
    delivery_time = models.CharField(max_length=20, choices=STATUS_CHOICES, default='1 día')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    image2 = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    image3 = models.ImageField(upload_to='images/', default='images/default_p_img.jpg', null=True)
    price = models.IntegerField(default=0, null=True)
    is_active = models.BooleanField(default=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    favorite = models.ManyToManyField(User, related_name='favorites', blank=True)
    likes = models.ManyToManyField(User, related_name='likes')
    dislikes = models.ManyToManyField(User, related_name='dislikes')

    def related_products(self):
        return Post.objects.filter(category=self.category).exclude(id=self.id).order_by('?')[:5]
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

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

    def __str__(self) -> str:
        return str(self.user) + ' -> ' + str(self.post)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    reciepient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    body = models.TextField()
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def send_message(from_user, to_user, body, file=None):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            reciepient=to_user,
            body=body,
            is_read=True,
        )

        if file:
            sender_message.file = file

        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            reciepient=from_user,
            body=body,
            is_read=False,
        )

        if file:
            recipient_message.file = sender_message.file  # Use the file saved in the sender_message

        recipient_message.save()
        return sender_message
    
    def get_message(user):
        users = []
        messages = Message.objects.filter(user=user).values('reciepient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                    'user': User.objects.get(pk=message['reciepient']),
                    'last': message['last'],
                    'unread': Message.objects.filter(user=user, reciepient__pk=message['reciepient'], is_read=False).count()
                })
        return users