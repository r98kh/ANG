# Generated by Django 3.2.12 on 2022-10-26 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]