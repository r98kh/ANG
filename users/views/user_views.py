from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q

import random

from users.models import *
from users.forms import *
from base.utils import *


@login_required(login_url='/users/login/')
def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        zipcode = request.POST.get('zipcode')
        mobile = request.POST.get('mobile')

        if profile.role == '1':
            private = profile.private
            form = PrivateEditForm(request.POST, instance=private)
        elif profile.role == '2':
            legal = profile.legal
            form = LegalEditForm(request.POST, instance=legal)

        if form.is_valid():
            profile.birth_date = birth_date
            profile.address = address
            profile.state = State.objects.get(state_id=state)
            profile.city = City.objects.get(id=city)
            profile.zipcode = zipcode
            if Profile.objects.filter(mobile=mobile).exclude(user=request.user).exists():
                messages.error(request, 'شماره همراه قبلا ثبت شده است')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                profile.mobile = mobile
            profile.save()

            form.save()
            messages.success(request, 'پروفایل ویرایش شد')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if profile.role == "1":
            private = profile.private
            form = PrivateEditForm(request.POST or None, instance=private)
        elif profile.role == '2':
            legal = profile.legal
            form = LegalEditForm(request.POST or None, instance=legal)

    states = State.objects.all()
    context = {'form': form, 'profile': profile, 'states': states}
    return render(request, 'profile/profile.html', context)


def register(request):
    mobile = request.COOKIES.get('mobile')
    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')

        user = User.objects.get(username=mobile)

        if 'private' in request.POST:
            form = PrivateForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.profile = user.profile
                instance.save()
                role = "1"
        elif 'legal' in request.POST:
            form = LegalForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.profile = user.profile
                instance.save()
                role = "2"

        Profile.objects.filter(user=user).update(birth_date=birth_date, address=address,
                                                 state=State.objects.get(
                                                     state_id=state),
                                                 city=City.objects.get(id=city), zipcode=zipcode,
                                                 role=role)
        user.is_active = True
        user.save()

        # send notification to user
        # send_user_notification(instance, 'register')

        login(request, user)
        res = redirect('/')
        res.delete_cookie('mobile')
        res.delete_cookie('next')
        return res
    else:
        states = State.objects.all()
        p_form = PrivateForm()
        l_form = LegalForm()
        
    if not mobile:
        raise Http404
    context = {'p_form': p_form, 'l_form': l_form, 'states': states}
    return render(request, 'auth/register.html', context)


def user_login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        if mobile and len(mobile) == 11 and mobile.isnumeric():
            q = Profile.objects.filter(mobile=mobile, user__is_active=True)

            code = random.randint(10000, 99999)

            if q.exists():
                if q[0].role == '1':
                    name = q[0].private.fname
                elif q[0].role == '2':
                    name = q[0].legal.fname
                    
                redirect_next = 'login'
                q.update(login_code=code)
                
            else:
                redirect_next = 'register'
                user, created = User.objects.get_or_create(
                    username=mobile, is_active=False)

                profile, created = Profile.objects.get_or_create(user=user)
                profile.login_code = code
                profile.mobile = mobile
                profile.save()
                name = 'کاربر عزیز'

            # send sms code
            result = send_confirmation_code(name, str(code), mobile)
            if result and result.status == 'active':
                res = HttpResponseRedirect('/users/confirm/')
                res.set_cookie('mobile', mobile)
                res.set_cookie('next', redirect_next)
                return res
            else:
                messages.error(request, 'خطا در ارسال پیامک. لطفا مجددا تلاش کنید')
        else:
            messages.error(request, 'شماره همراه معتبر نمیباشد')
    return render(request, 'auth/login.html')


def confirm(request):
    mobile = request.COOKIES.get('mobile')
    next = request.COOKIES.get('next')
    if request.method == 'POST':
        code = request.POST.get('code')
        if mobile and code:
            if next == 'login':
                q = Profile.objects.filter(mobile=mobile, login_code=code)
                if q.exists():
                    user = User.objects.get(username=mobile)
                    login(request, user)
                    
                    res = redirect('/')
                    res.delete_cookie('mobile')
                    res.delete_cookie('next')
                    return res
                else:
                    messages.error(request, 'کد تایید صحیح نیست')

            elif next == 'register':
                q = Profile.objects.filter(
                    user__username=mobile, login_code=code)
                if q.exists():
                    return redirect('register')
                else:
                    messages.error(request, 'کد تایید صحیح نیست')
        else:
            messages.error(request, 'خطایی رخ داده است. مجددا سعی کنید')

    return render(request, 'auth/confirm.html', {'mobile': mobile})


class UserList(PermissionRequiredMixin, ListView):
    model = User
    permission_required = "auth.view_user"
    template_name = "users/list.html"
    paginate_by = 10
    context_object_name = 'users'

    def get_queryset(self):
        users = User.objects.filter(
            is_superuser=False, expert__id=None).order_by('-date_joined')

        q = self.request.GET.get('q')
        role = self.request.GET.get('role')
        status = self.request.GET.get('status')
        sort = self.request.GET.get('sort')
        expert = self.request.GET.get('expert')

        if q:
            private_ids = list(Private.objects.filter(
                Q(fname__contains=q) | Q(lname__contains=q)).values_list('profile__id', flat=True)) + \
                list(Profile.objects.filter(
                    mobile__contains=q).values_list('id', flat=True))

            legal_ids = list(Legal.objects.filter(
                Q(fname__contains=q) | Q(lname__contains=q)).values_list('profile__id', flat=True)) + \
                list(Profile.objects.filter(
                    mobile__contains=q).values_list('id', flat=True))

            ids = private_ids + legal_ids
            users = users.filter(profile__id__in=ids)

        if expert:
            users = users.filter(profile__expert__id=expert)

        if role:
            users = users.filter(profile__role=role)

        if status:
            if status == 'active':
                users = users.filter(is_active=True)
            else:
                users = users.filter(is_active=False)

        if sort:
            if sort == 'asc':
                users = users.order_by('date_joined')
            elif sort == 'desc':
                users = users.order_by('-date_joined')

        return users

    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        context['experts'] = Expert.objects.filter(
            user__is_active=True).order_by('-user__date_joined')
        return context


@permission_required('auth.add_user', login_url='/admin/login/')
def add(request):
    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        mobile = request.POST.get('mobile')
        expert = request.POST.get('expert')

        if User.objects.filter(username=mobile).exists():
            messages.error(request, 'کاربر با این شماره همراه ثبت شده است')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            user = User.objects.create(username=mobile)
            profile = Profile.objects.create(user=user, mobile=mobile)

        if 'private' in request.POST:
            role = "1"
            form = PrivateForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.profile = profile
                instance.save()
            else:
                messages.error(request, form.errors)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        elif 'legal' in request.POST:
            role = "2"
            form = LegalForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.profile = profile
                instance.save()
            else:
                messages.error(request, form.errors)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        profile.birth_date = birth_date
        profile.address = address
        profile.state = State.objects.get(state_id=state)
        profile.city = City.objects.get(id=city)
        profile.zipcode = zipcode
        profile.role = role
        if expert:
            profile.expert = Expert.objects.get(id=expert)
        profile.save()

        # send notification to user
        # send_user_notification(instance, 'register')

        messages.success(request, 'مشتری ایجاد شد')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        states = State.objects.all()
        p_form = PrivateForm()
        l_form = LegalForm()

    experts = Expert.objects.filter(user__is_active=True)
    context = {'p_form': p_form, 'l_form': l_form,
               'states': states, 'experts': experts}
    return render(request, 'users/add.html', context)


@permission_required('auth.view_user', login_url='/admin/login/')
def edit(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        zipcode = request.POST.get('zipcode')
        mobile = request.POST.get('mobile')
        expert = request.POST.get('expert')
        status = request.POST.get('status')

        if profile.role == '1':
            private = profile.private
            form = PrivateEditForm(request.POST, instance=private)
        elif profile.role == '2':
            legal = profile.legal
            form = LegalEditForm(request.POST, instance=legal)

        if form.is_valid():
            if Profile.objects.filter(mobile=mobile).exclude(user=profile.user).exists():
                messages.error(request, 'شماره همراه قبلا ثبت شده است')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                profile.mobile = mobile

            profile.birth_date = birth_date
            profile.address = address
            profile.state = State.objects.get(state_id=state)
            profile.city = City.objects.get(id=city)
            profile.zipcode = zipcode
            if expert:
                profile.expert = Expert.objects.get(id=expert)
            profile.save()

            user.is_active = status
            user.save()

            form.save()
            messages.success(request, 'پروفایل ویرایش شد')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        if profile.role == "1":
            private = profile.private
            form = PrivateEditForm(request.POST or None, instance=private)
        elif profile.role == '2':
            legal = profile.legal
            form = LegalEditForm(request.POST or None, instance=legal)

    states = State.objects.all()
    experts = Expert.objects.filter(user__is_active=True)

    context = {'form': form, 'profile': profile,
               'user': user, 'states': states, 'experts': experts}
    return render(request, 'users/edit.html', context)
