# Generated by Django 5.1.2 on 2024-10-21 11:53

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='archive_app.subject'),
        ),
        migrations.CreateModel(
            name='Verification_Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expires_by', models.DateTimeField(default=datetime.datetime(2024, 10, 21, 11, 58, 42, 586485, tzinfo=datetime.timezone.utc))),
                ('code', models.CharField(max_length=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_code', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
