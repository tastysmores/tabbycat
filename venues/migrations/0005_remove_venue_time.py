# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-29 12:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0004_auto_20160228_1838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venue',
            name='time',
        ),
    ]