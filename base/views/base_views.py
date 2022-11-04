from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from base.models import Order


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def dashboard_admin(request):
    users = User.objects.filter(is_staff=False).count()
    if request.user.is_superuser:
        orders = Order.objects.filter(completed=True).order_by('-createdAt')
    else:
        orders = Order.objects.filter(
            user__profile__expert=request.user.expert)
    context = {'users': users, 'orders': orders}
    return render(request, 'dashboard_admin.html', context)


@login_required(login_url='/users/login/')
def dashboard_user(request):
    orders = Order.objects.filter(
        user=request.user, completed=True).order_by('-createdAt')

    context = {'orders': orders}
    return render(request, 'dashboard_user.html', context)
