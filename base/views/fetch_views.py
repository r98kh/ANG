from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core import serializers
from django.db.models import Max
from django.core.files.storage import FileSystemStorage

import json
import random

from base.models import *
from base.utils import *
from users.models import *


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def feature_add(request):
    data = json.loads(request.body)
    f_name = data['feature_name']

    if Feature.objects.filter(name=f_name).exists():
        message = {'status_code': '400', 'text': 'مشخصه وجود دارد'}
    else:
        Feature.objects.create(name=f_name)
        message = {'status_code': '200', 'text': 'مشخصه ایجاد شد'}

    features = list(Feature.objects.filter(is_active=True).values())
    return JsonResponse({'message': message, 'features': features}, safe=False)

def filter_color(request):
    productId = request.GET.get('productId')

    colors = ProductColor.objects.filter(product_id=productId)

    t = render_to_string('product/ajax/color-list.html', {'colors': colors})
    return JsonResponse({'data': t})


def get_product_features(request):
    productId = request.GET.get('productId')
    product = Product.objects.get(id=productId)

    colors = ProductColor.objects.filter(product=product)

    featurevalues = ProductFeatureValue.objects.filter(product_id=productId).values('featurevalue__feature__id',
                                                                                    'featurevalue__feature__perName',
                                                                                    'featurevalue__id',
                                                                                    'featurevalue__name').order_by('priority')

    t = render_to_string('order/ajax/features.html',
                         {'featurevalues': featurevalues, 'product': product, 'colors': colors})
    return JsonResponse({'data': t})


@login_required(login_url='users/login/')
def pre_order_edit(request):
    data = json.loads(request.body)
    itemId = data['itemId']
    quantity = data['quantity']
    colorId = data['color']
    featureValueIdList = data['featureValueIdList']

    color = Color.objects.get(id=colorId)
    for i in featureValueIdList:
        orderitemdetailId = i.split("|")[0]
        featureId = i.split("|")[1]
        featureValueId = i.split("|")[2]

        feature = Feature.objects.get(id=featureId)
        featureValue = FeatureValue.objects.get(id=featureValueId)

        OrderItemDetail.objects.filter(id=orderitemdetailId).update(
            feature=feature, featureName=feature.perName, featureValue=featureValue, featureValueName=featureValue.name)

        OrderItem.objects.filter(id=itemId).update(
            quantity=quantity, color=color, colorName=color.name)

        message = {'status': 'success', 'text': 'سفارش با موفقیت ویرایش شد'}

    return JsonResponse(message, safe=False)


@login_required(login_url='users/login/')
def pre_order_delete(request):
    data = json.loads(request.body)
    itemId = data['itemId']
    OrderItem.objects.filter(id=itemId).delete()

    message = {'status': 'success', 'text': 'محصول از سبد سفارش حذف شد'}
    return JsonResponse(message, safe=False)


@login_required(login_url='users/login/')
def order_complete(request):
    data = json.loads(request.body)
    orderId = data['orderId']
    action = data['action']
    trans_id = random.randint(1000000, 9999999)

    order = Order.objects.get(id=orderId)
    order.transId = trans_id
    order.completed = True

    if action == 'cancel':
        order.track = 'CANCEL'
        status = 'success'
        title = 'لغو سفارش'
        text = 'سفارش لغو شد'
    else:
        order.track = 'REGISTER'
        status = 'success'
        title = 'تکمیل سفارش'
        text = 'سفارش باموفقیت ثبت شد'
    order.save()

    message = {'status': status, 'title': title, 'text': text}

    # send notification to user
    # send_order_notification(order, 'register', None)
    # send sms to user
    return JsonResponse(message, safe=False)


@login_required(login_url='users/login/')
def admin_order_complete(request):
    data = json.loads(request.body)
    orderId = data['orderId']
    order = Order.objects.get(id=orderId)
    trans_id = random.randint(10000, 99999)
    order.transaction_id = trans_id
    order.completed = True
    order.save()

    # send notification to user
    send_order_notification(order, 'register', '')
    # send sms to user
    res = JsonResponse("ok", safe=False)
    res.delete_cookie('myId')
    return res


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def order_change_status(request):
    data = json.loads(request.body)

    order_id = data['orderId']
    trackValue = data['trackValue']
    track_name = data['trackName']

    order = Order.objects.get(id=order_id)

    # send_order_notification(order, 'change', track_name)
    # send_change_order_to_user(
    #     track_id, order.user.profile.mobile, order.user.profile.get_full_name)
    order.track = trackValue
    order.save()
    return JsonResponse({'status': 200}, safe=False)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def update_status(request):
    data = json.loads(request.body)
    id = data['id']
    status = data['value']
    db = data['db']

    if db == 'users' or db == 'expert':
        q = User.objects.filter(id=id)

    if status:
        q.update(is_active=True)
        message = {'status': 'success', 'text': 'وضعیت فعال شد'}
    else:
        q.update(is_active=False)
        message = {'status': 'success', 'detail': 'وضعیت غیرفعال شد'}

    return JsonResponse(message, safe=False)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
def featurevalue_edit(request):
    data = json.loads(request.body)
    name = data['name']
    code = data['code']
    id = data['id']
    productId = data['product']

    FeatureValue.objects.filter(id=id).update(name=name, code=code)
    ProductFeatureValue.objects.filter(
        featurevalue_id=id).update(product_id=productId)

    message = {'status': '200', 'text': 'مشخصه محصول ویرایش شد'}
    return JsonResponse(message, safe=False)


def get_city(request):
    state = request.GET.get('state')

    data = serializers.serialize('json', City.objects.filter(state=state))
    return HttpResponse(data, content_type="application/json")


def get_features(request):
    per_feature_names = list(Feature.objects.filter(
        isActive=True).values_list('perName', flat=True))
    eng_feature_names = list(Feature.objects.filter(
        isActive=True).values_list('engName', flat=True))

    return HttpResponse(json.dumps({'per_feature_names': per_feature_names, 'eng_feature_names': eng_feature_names}))


def get_feature_details(request):
    featureName = request.GET.get('featureName')
    productId = request.GET.get('productId')

    feature_details = list(Feature.objects.filter(
        perName=featureName).values_list('engName', flat=True))

    if feature_details:
        feature_details = feature_details[0]
    else:
        feature_details = None

    priority = list(ProductFeatureValue.objects.filter(
        product_id=productId,
        featurevalue__feature__perName=featureName).values_list('priority', flat=True).distinct())

    if priority:
        priority = priority[0]
    else:
        priority = ProductFeatureValue.objects.filter(
            product_id=productId).aggregate(priority=Max('priority'))
        priority = int(priority['priority']) + 1

    return HttpResponse(json.dumps({'engFeatureName': feature_details, 'priority': priority}))
