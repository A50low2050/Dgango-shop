from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from .models import Categories, Product, CartProduct
from .forms import RegisterForm, AuthenticationUserForm
from django.contrib.contenttypes.models import ContentType
from .mixins import *


class HomePage(CartMixin, ListView):
    model = Categories
    template_name = 'shop/home.html'
    context_object_name = 'categories'
    extra_context = {'title': 'Home'}

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        search_query = self.request.GET.get('search-bar', '')
        context['query'] = search_query
        context['products'] = Product.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        context['cart'] = self.cart
        return context


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign Up'

        return context


class LoginUser(LoginView):
    form_class = AuthenticationUserForm
    template_name = 'shop/login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign In'

        return context


def logout_user(request):
    logout(request)
    return redirect('login')


class ShowProduct(DetailView):

    model = Product
    template_name = 'shop/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        product_slug = self.kwargs['product_slug']
        context['product'] = Product.objects.filter(slug=product_slug).first()
        return context


class ShowCategory(DetailView):
    model = Categories
    template_name = 'shop/home.html'
    slug_url_kwarg = 'category_slug'
    pk_url_kwarg = 'category_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_id']
        category_slug = self.kwargs['category_slug']

        context['cart'] = Cart.objects.filter(owner=self.request.user).first()
        context['category'] = Categories.objects.filter(slug=category_slug).first()
        context['categories'] = Categories.objects.all()
        context['products'] = Product.objects.filter(category=category_id)

        return context


class CartUser(CartMixin, View):

    def get(self, request, *args, **kwargs):

        context = {
            'title': 'Your Cart',
            'cart': self.cart,
        }

        return render(request, 'shop/cart.html', context)


class AddToCart(CartMixin, View):

    def get(self, request, *args, **kwargs):

        product_slug = self.kwargs['product_slug']
        content_type = ContentType.objects.get(model='product')
        user_product = content_type.model_class().objects.get(slug=product_slug)

        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=user_product.id
        )
        if created:
            self.cart.products.add(cart_product)
            messages.add_message(request, messages.INFO, f"You add success {user_product.title}")
        self.cart.save()
        return HttpResponseRedirect('/cart/')


class RemoveFromCart(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = self.kwargs['product_slug']
        content_type = ContentType.objects.get(model='product')
        user_product = content_type.model_class().objects.get(slug=product_slug)

        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=user_product.id
        )

        self.cart.products.remove(cart_product)
        cart_product.delete()
        self.cart.save()
        messages.add_message(request, messages.INFO, f"You success remove {user_product.title}")
        return HttpResponseRedirect('/cart/')


class ChangeQtyProduct(CartMixin, View):

    def post(self, request, product_slug):
        content_type = ContentType.objects.get(model='product')
        user_product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=user_product.id
        )
        qty = int(request.POST['qty'])
        cart_product.quality = qty
        cart_product.save()
        self.cart.save()
        messages.add_message(request, messages.INFO, f"You change quality {user_product.title}")
        return HttpResponseRedirect('/cart/')