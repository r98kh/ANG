# Generated by Django 3.2.12 on 2022-10-20 15:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=300)),
                ('text', models.CharField(max_length=500)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('track', models.CharField(max_length=10)),
                ('transId', models.CharField(max_length=10)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productName', models.CharField(max_length=300)),
                ('colorName', models.CharField(blank=True, max_length=100, null=True)),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('color', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.color')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_request', models.CharField(blank=True, max_length=500, null=True)),
                ('manager_decision', models.CharField(blank=True, max_length=200, null=True)),
                ('final_decision', models.CharField(blank=True, max_length=200, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItemDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featureName', models.CharField(max_length=300)),
                ('featureValueName', models.CharField(max_length=300)),
                ('feature', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.feature')),
                ('featureValue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.featurevalue')),
                ('orderitem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.orderitem')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('read', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.notification')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('read', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('notification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.notification')),
            ],
        ),
        migrations.CreateModel(
            name='DamagedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(blank=True, max_length=10, null=True)),
                ('problem_count', models.CharField(max_length=5)),
                ('quality_problem', models.CharField(max_length=100)),
                ('orderitem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.orderitem')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
                ('report', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.report')),
            ],
        ),
    ]