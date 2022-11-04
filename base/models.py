from django.db import models
from django.contrib.auth.models import User

from product.models import *


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    track = models.CharField(max_length=10)
    transId = models.CharField(max_length=10)

    def __str__(self):
        return self.user.profile.get_full_name

    @property
    def get_track(self):
        if self.track == 'REGISTER':
            return 'ثبت سفارش'
        elif self.track == 'HOLDING':
            return 'در انتظار تایید سفارش'
        elif self.track == 'PRODUCING':
            return 'در حال تولید'
        elif self.track == 'PAYING':
            return 'در انتظار تکمیل وجه'
        elif self.track == 'COMPLETE':
            return 'تکمیل سفارش'
        elif self.track == 'CANCEL':
            return 'لغو سفارش'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    productName = models.CharField(max_length=300)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    colorName = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.productName}*{self.quantity}'


class OrderItemDetail(models.Model):
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.SET_NULL, null=True)
    featureName = models.CharField(max_length=300)
    featureValue = models.ForeignKey(
        FeatureValue, on_delete=models.SET_NULL, null=True)
    featureValueName = models.CharField(max_length=300)


class Notification(models.Model):
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=300)
    text = models.CharField(max_length=500)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class NotificationUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notification = models.ForeignKey(
        Notification, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=500)
    read = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)


class NotificationAdmin(models.Model):
    notification = models.ForeignKey(
        Notification, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=500)
    read = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    customer_request = models.CharField(max_length=500, blank=True, null=True)
    manager_decision = models.CharField(max_length=200, blank=True, null=True)
    final_decision = models.CharField(max_length=200, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)


class DamagedProduct(models.Model):
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True)
    orderitem = models.ForeignKey(
        OrderItem, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.CharField(max_length=10, blank=True, null=True)
    problem_count = models.CharField(max_length=5)
    quality_problem = models.CharField(max_length=100)
