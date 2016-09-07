# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-07 10:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('content', models.TextField()),
                ('update_at', models.DateTimeField()),
                ('download_at', models.DateTimeField()),
                ('url', models.CharField(max_length=1024, unique=True)),
                ('hash', models.CharField(default='', max_length=1024)),
                ('rank', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, max_length=100)),
                ('start', models.IntegerField(default=0)),
                ('end', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=1)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search.Page')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='word',
            unique_together=set([('word', 'page')]),
        ),
    ]
