from django.contrib import admin
from django.forms import ModelForm, ValidationError
from .models import *
from django.utils.safestring import mark_safe
from PIL import Image


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'login', 'email', 'password', 'data_register')
    list_display_links = ('id', 'login', 'email')
    search_fields = ('id', 'login', 'email')


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'description', 'image_show', 'time_create', 'time_update', 'category')
    list_display_links = ('id', 'title', 'description', 'category')
    search_fields = ('id', 'title', 'description', 'category')
    prepopulated_fields = {'slug': ('title',)}

    def image_show(self, obj):
        if obj.photo:
            return mark_safe("<img src='{}' width='60'/>".format(obj.photo.url))
        return None
    image_show.__name__ = 'icon'


class NoteBookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].help_text = mark_safe(
            '<span style="color:red; font-size:14px;">'
            'Upload an image with a minimum resolution {}x{}</span>'.format(*Product.MIN_RESOLUTION),
        )

    def clean(self):
        photo = self.cleaned_data['photo']
        img = Image.open(photo)
        min_height, min_width = Product.MIN_RESOLUTION
        max_height, max_width = Product.MAX_RESOLUTION

        if photo.size > Product.MAX_SIZE_IMAGE:
            raise ValidationError('The image size must not exceed 5MB')
        if img.height < min_height or img.width < min_width:
            raise ValidationError('The uploaded image is less than the minimum {}x{}!'.format(*Product.MIN_RESOLUTION))

        if img.height > max_height or img.width > max_width:
            raise ValidationError('The uploaded image is more than the maximum {}x{}!'.format(*Product.MAX_RESOLUTION))


class CartAdmin(admin.ModelAdmin):

    list_display = ('id', 'owner', 'get_products', 'total_products', 'final_price', 'for_anonymous_user')

    list_display_links = ('id', 'owner', 'get_products')
    search_fields = ('owner', 'get_products')

    def get_products(self, obj):
        return "\n".join([str(p.content_object) for p in obj.products.all()])
    get_products.__name__ = 'products'


class CartProductAdmin(admin.ModelAdmin):

    list_display = ('id', 'user', 'content_object', 'content_type', 'object_id', 'quality', 'final_price')
    list_display_links = ('id','user', 'content_object', 'content_type', 'object_id')
    search_fields = ('user', 'content_object')


admin.site.register(User, ShopAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartProduct, CartProductAdmin)

