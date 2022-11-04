from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin

import random

from base.models import *
from base.utils import *
from product.models import *
from users.models import *


class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class OrderList(ListView):
    model = Order
    template_name = "order/list.html"
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        orders = Order.objects.filter(
            completed=True, user=self.request.user).order_by('-createdAt')

        q = self.request.GET.get('q')
        track = self.request.GET.get('track')
        sort = self.request.GET.get('sort')

        if q:
            orders = orders.filter(Q(user__profile__private__fname__icontains=q) |
                                   Q(user__profile__legal__fname__icontains=q) | Q(user__profile__private__lname__icontains=q) |
                                   Q(user__profile__legal__lname__icontains=q) | Q(user__profile__mobile__contains=q) | Q(transId__contains=q))

        if track:
            orders = orders.filter(track=track)

        if sort:
            if sort == 'asc':
                orders = orders.order_by('createdAt')
            elif sort == 'desc':
                orders = orders.order_by('-createdAt')

        return orders


class AdminOrderList(AdminStaffRequiredMixin, ListView):
    model = Order
    permission_required = 'base.view_order'
    template_name = "order/list.html"
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_superuser:
            orders = Order.objects.filter(
                completed=True).order_by('-createdAt')
        else:
            orders = Order.objects.filter(
                user__profile__expert=self.request.user.expert, completed=True).order_by('-createdAt')

        q = self.request.GET.get('q')
        track = self.request.GET.get('track')
        sort = self.request.GET.get('sort')

        if q:
            orders = orders.filter(Q(user__profile__private__fname__icontains=q) |
                                   Q(user__profile__legal__fname__icontains=q) | Q(user__profile__private__lname__icontains=q) |
                                   Q(user__profile__legal__lname__icontains=q) | Q(user__profile__mobile__contains=q) | Q(transId__contains=q))

        if track:
            orders = orders.filter(track=track)

        if sort:
            if sort == 'asc':
                orders = orders.order_by('createdAt')
            elif sort == 'desc':
                orders = orders.order_by('-createdAt')

        return orders


@login_required(login_url='/users/login/')
def add(request):
    if request.method == 'POST':
        productId = request.POST.get('product')
        colorId = request.POST.get('color')
        quantity = request.POST.get('quantity')
        productFeatureValues = request.POST.getlist('productfeaturevalue')

        if not productId:
            messages.error(request, 'محصول را انتخاب کنید')
        elif not productFeatureValues:
            messages.error(request, 'مشخصه محصول را به درستی انتخاب نکرده اید')
        elif not quantity:
            messages.error(request, 'فیلد تعداد ضروری میباشد')
        else:
            order, created = Order.objects.get_or_create(
                user=request.user, completed=False)
            product = Product.objects.get(id=productId)

            code = ''
            if colorId:
                color = Color.objects.get(id=colorId)
                if color.productCode:
                    code += color.productCode
                colorName = color.name
            else:
                color = None
                colorName = None

            exists = check_if_product_exists(
                productId, productFeatureValues, color)

            if exists:
                orderitem = OrderItem.objects.get(id=exists)
                orderitem.quantity = orderitem.quantity + int(quantity)
                orderitem.save()
            else:
                orderitem = OrderItem.objects.create(order=order, product_id=productId, productName=product.perName,
                                                     quantity=quantity, color=color, colorName=colorName)
                for i in productFeatureValues:
                    featureId = i.split('|')[0]
                    featureValueId = i.split('|')[1]

                    feature = Feature.objects.get(id=featureId)
                    featureValue = FeatureValue.objects.get(id=featureValueId)
                    if featureValue.code:
                        code += featureValue.code

                    OrderItemDetail.objects.create(orderitem=orderitem, feature=feature,
                                                   featureName=feature.perName, featureValue=featureValue,
                                                   featureValueName=featureValue.name)

                orderitem.code = code
                orderitem.save()
            messages.success(request, 'سفارش ثبت شد')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    products = Product.objects.filter(isActive=True).order_by('-createdAt')
    order = Order.objects.filter(completed=False).last()
    items = OrderItem.objects.filter(order=order)
    context = {'products': products, 'order': order, 'items': items}
    return render(request, 'order/add.html', context)


@permission_required('base.add_order', login_url='/admin/login/')
def admin_add(request):
    if request.method == 'POST':
        productId = request.POST.get('product')
        colorId = request.POST.get('color')
        customer = request.POST.get('customer')
        quantity = request.POST.get('quantity')
        productFeatureValues = request.POST.getlist('productfeaturevalue')

        # user = User.objects.get(profile__id=profile_id)

        # cookie_id = request.COOKIES.get('myId')
        # if cookie_id:
        # profile = Profile.objects.get(id=cookie_id)
        # if profile_id != cookie_id:
        # messages.error(
        # request, f'سفارش مشتری {profile.get_full_name} تکمیل نشده است لطفا ابتدا سفارش قبلی را تکمیل کنید')
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not productId:
            messages.error(request, 'محصول را انتخاب کنید')
        elif not productFeatureValues:
            messages.error(request, 'مشخصه محصول را به درستی انتخاب نکرده اید')
        elif not quantity:
            messages.error(request, 'فیلد تعداد ضروری میباشد')
        else:
            order, created = Order.objects.get_or_create(
                user_id=customer, completed=False)
            product = Product.objects.get(id=productId)

            code = ''
            if colorId:
                color = Color.objects.get(id=colorId)
                if color.productCode:
                    code += color.productCode
                colorName = color.name
            else:
                color = None
                colorName = None

            exists = check_if_product_exists(
                productId, productFeatureValues, color)

            if exists:
                orderitem = OrderItem.objects.get(id=exists)
                orderitem.quantity = orderitem.quantity + int(quantity)
                orderitem.save()
            else:
                orderitem = OrderItem.objects.create(order=order, product_id=productId, productName=product.perName,
                                                     quantity=quantity, color=color, colorName=colorName)
                for i in productFeatureValues:
                    featureId = i.split('|')[0]
                    featureValueId = i.split('|')[1]

                    feature = Feature.objects.get(id=featureId)
                    featureValue = FeatureValue.objects.get(id=featureValueId)
                    if featureValue.code:
                        code += featureValue.code

                    OrderItemDetail.objects.create(orderitem=orderitem, feature=feature,
                                                   featureName=feature.perName, featureValue=featureValue,
                                                   featureValueName=featureValue.name)

                orderitem.code = code
                orderitem.save()
            messages.success(request, 'سفارش ثبت شد')

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # profile_id = request.COOKIES.get('myId')
    # if profile_id:
        # user = User.objects.get(profile__id=profile_id)
        # order, created = Order.objects.get_or_create(
            # user=user, completed=False)
        # items = OrderItem.objects.filter(order=order).values('id', 'product__name', 'quantity', 'group_id', 'product_feature__feature__name',
            #  'product_feature_value__feature_value__name', 'product_feature_value__feature_value__image',
            #  'product_feature__feature__id', 'code', 'product_feature_value__id').annotate(Count('group_id'))
    # else:
    #     order = None
    #     items = []

    products = Product.objects.filter(isActive=True).order_by('-createdAt')
    users = User.objects.filter(
        is_active=True, is_staff=False).order_by('-date_joined')

    order = Order.objects.filter(completed=False).last()
    items = OrderItem.objects.filter(order=order)
    context = {'products': products, 'users': users,
               'order': order, 'items': items}
    return render(request, 'order/admin/add.html', context)


@ login_required(login_url='/users/login/')
def detail(request, order_id):
    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()
    context = {'order': order, 'items': items}
    return render(request, 'order/detail.html', context)


@ login_required(login_url='/users/login/')
def invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = order.orderitem_set.all()
    context = {'order': order, 'items': items}
    return render(request, 'order/invoice.html', context)
