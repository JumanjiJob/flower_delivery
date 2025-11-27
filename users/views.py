from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from orders.models import Order
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматический вход после регистрации
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, f'Аккаунт {username} успешно создан!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Личный кабинет пользователя"""
    # Получаем статистику заказов пользователя
    orders = Order.objects.filter(user=request.user)
    orders_stats = {
        'total': orders.count(),
        'new': orders.filter(status='new').count(),
        'confirmed': orders.filter(status='confirmed').count(),
        'processing': orders.filter(status='processing').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'delivered': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }

    # Последние заказы
    recent_orders = orders.order_by('-created_at')[:5]

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders_stats': orders_stats,
        'recent_orders': recent_orders,
    }

    return render(request, 'users/profile.html', context)


@login_required
def order_history(request):
    """Полная история заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_filter': status_filter,
    }

    return render(request, 'users/order_history.html', context)


@login_required
def home(request):
    """Домашняя страница для авторизованных пользователей"""
    # Получаем статистику для быстрого обзора
    orders = Order.objects.filter(user=request.user)
    recent_orders = orders.order_by('-created_at')[:3]

    context = {
        'recent_orders': recent_orders,
        'total_orders': orders.count(),
        'active_orders': orders.exclude(status__in=['delivered', 'cancelled']).count(),
    }

    return render(request, 'users/home.html', context)


def landing(request):
    """Главная страница для неавторизованных пользователей"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'users/landing.html')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)