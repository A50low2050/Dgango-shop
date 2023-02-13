from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from PIL import Image
from django.urls import reverse

UsersModel = get_user_model()


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class User(models.Model):
    login = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.IntegerField()
    repeat_password = models.IntegerField()
    data_register = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'User'
        ordering = ['data_register']


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (900, 900)
    MAX_SIZE_IMAGE = 5242880

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='product_photo')
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    old_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    category = models.ForeignKey('Categories', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('show_product', kwargs={'product_slug': self.slug})

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Product'
        ordering = ['time_create']

    def save(self, *args, **kwargs):
        photo = self.photo
        img = Image.open(photo)
        min_height, min_width = self.MIN_RESOLUTION
        max_height, max_width = self.MAX_RESOLUTION

        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('The uploaded image is less than the minimum!')

        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('The uploaded image is more than the maximum!')
        super().save(*args, **kwargs)


class Categories(models.Model):
    icon = models.ImageField(upload_to='category_icon')
    name = models.CharField(max_length=30, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('show_category', kwargs={'category_slug': self.slug, 'category_id': self.pk})

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Category'
        ordering = ['name']


class CartProduct(models.Model):
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    quality = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return str(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.quality * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'CartProduct'
        verbose_name_plural = 'CartProduct'


class Cart(models.Model):

    owner = models.ForeignKey(UsersModel, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        id_cart = self.id
        if id_cart:
            cart_data = self.products.aggregate(models.Sum('final_price'), models.Count('id'))
            if cart_data.get('final_price__sum'):
                self.final_price = cart_data['final_price__sum']
            else:
                self.final_price = 0
            self.total_products = cart_data['id__count']
            super().save(*args, **kwargs)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Cart'

