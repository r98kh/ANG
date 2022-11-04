from .models import *
from ippanel import Client


def send_order_notification(order, subject, track_name):

    noti = Notification.objects.get(title='order', subject=subject)
    text = noti.text.replace('transaction_id', str(order.transaction_id))
    if track_name:
        text = text.replace('track', track_name)
    NotificationUser.objects.create(
        user=order.user, notification=noti, text=text)
    NotificationAdmin.objects.create(notification=noti, text=text)


def send_user_notification(instance, subject):
    if instance:
        noti = Notification.objects.get(title='user', subject=subject)
        text = noti.text.replace('fname', str(instance.fname))
        NotificationUser.objects.create(
            user=instance.profile.user, notification=noti, text=text)
        NotificationAdmin.objects.create(
            notification=noti, text='مشتری جدیدی ثبت نام کرد')


def send_confirmation_code(name, code, mobile):
    api_key = 'oV49VQNYQv37gwIQsYjAJp8URE3RgL-z06w2sUfTiEY='
    sms = Client(api_key)
    pattern_values = {
        "name": name,
        "code": code,
    }

    try:
        bulk_id = sms.send_pattern(
            "k58n4blrcu",    # pattern code
            "3000505",      # originator
            mobile,  # recipient
            pattern_values,  # pattern values
        )
        message = sms.get_message(bulk_id)
        return message
    except:
        return False


def send_password_to_expert(mobile, password, username):
    api_key = 'oV49VQNYQv37gwIQsYjAJp8URE3RgL-z06w2sUfTiEY='
    sms = Client(api_key)
    pattern_values = {
        "username": username,
        "password": password,
    }

    bulk_id = sms.send_pattern(
        "dsiwn1or8jlv6yh",    # pattern code
        "3000505",      # originator
        mobile,  # recipient
        pattern_values,  # pattern values
    )


def send_change_order_to_user(track_id, mobile, name):
    api_key = 'oV49VQNYQv37gwIQsYjAJp8URE3RgL-z06w2sUfTiEY='
    sms = Client(api_key)
    pattern_values = {
        "name": name,
    }
    if track_id == '1':
        pattern_code = "o4ew0y3xcmqt8no"
    elif track_id == '2':
        pattern_code = '4oxi9i1tkyoucl0'
    elif track_id == '3':
        pattern_code = 'kgcph62wxrypvv8'
    elif track_id == '4':
        pattern_code = 'zw2yf0vw1p421ey'
    elif track_id == '5':
        pattern_code = 'f6zu0tqc6yps0ew'

    bulk_id = sms.send_pattern(
        pattern_code,    # pattern code
        "3000505",      # originator
        mobile,  # recipient
        pattern_values,  # pattern values
    )


def check_if_product_exists(productId, featureValues, color):
    for i in featureValues:
        featureId = i.split('|')[0]
        featureValueId = i.split('|')[1]

        feature = Feature.objects.get(id=featureId)
        featureValue = FeatureValue.objects.get(id=featureValueId)
        q = OrderItemDetail.objects.filter(orderitem__order__completed=False,
                                           orderitem__product__id=productId,
                                           orderitem__color=color,
                                           featureName=feature.perName,
                                           featureValueName=featureValue.name)

        if not q.exists():
            return False

    return q[0].orderitem.id
