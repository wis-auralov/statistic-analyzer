# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-19 07:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0004_auto_20160115_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_block',
            field=models.BooleanField(default=False, verbose_name='\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'),
        ),
        migrations.AddField(
            model_name='historicalclient',
            name='is_block',
            field=models.BooleanField(default=False, verbose_name='\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d'),
        ),
    ]
