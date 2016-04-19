# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 10:22
from __future__ import unicode_literals

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StoredFormCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('description', models.TextField(blank=True, null=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('report_type', models.CharField(choices=[(b'kmclient_manage', '\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u043e\u0442\u0447\u0435\u0442 \u043f\u043e KM \u043a\u043b\u0438\u0435\u043d\u0442\u0443')], default=b'kmclient_manage', max_length=128, verbose_name='\u0422\u0438\u043f \u043e\u0442\u0447\u0435\u0442\u0430')),
                ('pickled_form', picklefield.fields.PickledObjectField(editable=False, verbose_name='\u0421\u0435\u0440\u0438\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u0430\u044f \u0444\u043e\u0440\u043c\u0430')),
                ('pickled_formset', picklefield.fields.PickledObjectField(editable=False, verbose_name='\u0421\u0435\u0440\u0438\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0444\u043e\u0440\u043c\u0441\u0435\u0442')),
            ],
            options={
                'verbose_name': '\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u0430\u044f \u0444\u043e\u0440\u043c\u0430',
                'verbose_name_plural': '\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435 \u0444\u043e\u0440\u043c\u044b',
            },
        ),
    ]
