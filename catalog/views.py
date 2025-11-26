from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category
from .forms import ProductFilterForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('category')

        # Фильтрация по категории
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            queryset = queryset.filter(category=category)

        # Фильтрация через форму
        self.form = ProductFilterForm(self.request.GET)
        if self.form.is_valid():
            category_id = self.form.cleaned_data.get('category')
            price_min = self.form.cleaned_data.get('price_min')
            price_max = self.form.cleaned_data.get('price_max')

            if category_id:
                queryset = queryset.filter(category_id=category_id)
            if price_min:
                queryset = queryset.filter(price__gte=price_min)
            if price_max:
                queryset = queryset.filter(price__lte=price_max)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['form'] = getattr(self, 'form', ProductFilterForm())

        # Текущая категория для breadcrumbs
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_available=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Похожие товары из той же категории
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id)[:4]
        return context


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'catalog/category_list.html', {'categories': categories})