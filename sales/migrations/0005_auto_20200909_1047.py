# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-09 02:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20200909_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='class_list',
            field=models.ManyToManyField(to='sales.ClassList', verbose_name='已报班级'),
        ),
    ]