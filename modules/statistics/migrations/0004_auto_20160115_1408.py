# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-15 11:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0003_auto_20151218_1427'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientactionlog',
            options={'verbose_name': '\u0421\u043e\u0431\u044b\u0442\u0438\u0435 \u041a\u041c-\u043a\u043b\u0438\u0435\u043d\u0442\u0430', 'verbose_name_plural': '\u0421\u043e\u0431\u044b\u0442\u0438\u044f \u041a\u041c-\u043a\u043b\u0438\u0435\u043d\u0442\u0430'},
        ),
        migrations.AlterModelOptions(
            name='dealer',
            options={'ordering': ['name'], 'verbose_name': '\u0414\u0438\u043b\u0435\u0440', 'verbose_name_plural': '\u0414\u0438\u043b\u0435\u0440\u044b'},
        ),
        migrations.AlterField(
            model_name='action',
            name='action_group',
            field=models.ManyToManyField(blank=True, to='statistics.ActionGroup', verbose_name='\u0413\u0440\u0443\u043f\u043f\u0430 \u0441\u043e\u0431\u044b\u0442\u0438\u0439'),
        ),
        migrations.AlterField(
            model_name='client',
            name='dealer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='statistics.Dealer', verbose_name='\u0414\u0438\u043b\u0435\u0440'),
        ),
        migrations.AlterField(
            model_name='client',
            name='login',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\u041b\u043e\u0433\u0438\u043d'),
        ),
        migrations.AlterField(
            model_name='clientactionlog',
            name='action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='statistics.Action', verbose_name='\u0421\u043e\u0431\u044b\u0442\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='clientactionlog',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='statistics.Client', verbose_name='\u041a\u041c-\u043a\u043b\u0438\u0435\u043d\u0442'),
        ),
        migrations.AlterField(
            model_name='historicalclient',
            name='login',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='\u041b\u043e\u0433\u0438\u043d'),
        ),
    ]
