# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-09-26 01:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker', models.CharField(blank=True, max_length=12, verbose_name='broker')),
                ('account_id', models.CharField(blank=True, max_length=12, verbose_name='account_id')),
                ('trade_id', models.CharField(max_length=12, verbose_name='trade_id')),
                ('instrument', models.CharField(max_length=12, verbose_name='instrument')),
                ('strategy_name', models.CharField(blank=True, max_length=12, verbose_name='strategy_name')),
                ('strategy_version', models.CharField(blank=True, max_length=12, verbose_name='strategy_version')),
                ('strategy_magic_number', models.IntegerField(blank=True, null=True, verbose_name='strategy_magic_number')),
                ('open_time', models.DateTimeField(blank=True, null=True, verbose_name='open time')),
                ('close_time', models.DateTimeField(blank=True, null=True, verbose_name='close time')),
                ('profitable_time', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='profitable time')),
                ('open_price', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True, verbose_name='open_price')),
                ('close_price', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True, verbose_name='close_price')),
                ('lots', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='lots')),
                ('pips', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='pips')),
                ('profit', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='profit')),
                ('max_profit', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='max_profit')),
                ('min_profit', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='min_profit')),
                ('drawdown', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True, verbose_name='min_profit')),
                ('risk', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='risk')),
            ],
        ),
    ]