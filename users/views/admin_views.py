from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from users.forms import AdminForm, PasswordChangeForm


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def profile(request):
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'کاربر ادمین ویرایش شد')
    else:
        form = AdminForm(request.POST or None, instance=request.user)

    context = {'form': form}
    return render(request, 'profile/admin/profile.html', context)


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard_admin')
            else:
                messages.error(request, 'نام کاربری یا رمز عبور صحیح نمیباشد')
        else:
            messages.error(request, 'خطایی رخ داده است')
    return render(request, 'auth/admin/login.html')


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'رمز عبور باموفقیت ثبت شد')
            return redirect('change_password')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'auth/admin/change_password.html', {
        'form': form
    })
