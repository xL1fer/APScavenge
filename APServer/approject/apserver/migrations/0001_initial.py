# Generated by Django 5.0.1 on 2024-03-30 12:11

import apserver.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgentStatus',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ip', models.CharField(max_length=32)),
                ('token', models.CharField(blank=True, max_length=128)),
                ('area', models.CharField(max_length=64, unique=True, validators=[apserver.models.area_validator])),
                ('alias_name', models.CharField(blank=True, max_length=64)),
                ('is_online', models.BooleanField(default=True)),
                ('is_attacking', models.BooleanField(default=False)),
                ('is_requesting', models.BooleanField(default=False)),
                ('last_heartbeat', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='InfoHistory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('user_type', models.CharField(blank=True, max_length=64)),
                ('user_info_id', models.BigIntegerField(blank=True, null=True)),
                ('capture_time', models.DateTimeField(auto_now_add=True)),
                ('area', models.CharField(max_length=64, validators=[apserver.models.area_validator])),
            ],
        ),
        migrations.CreateModel(
            name='Seizure',
            fields=[
                ('email', models.CharField(max_length=128, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PasswordHash',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('asleap', models.CharField(blank=True, max_length=256)),
                ('jtr', models.CharField(blank=True, max_length=256)),
                ('hashcat', models.CharField(blank=True, max_length=256)),
                ('info_history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='apserver.infohistory')),
            ],
        ),
        migrations.AddField(
            model_name='infohistory',
            name='seizure_email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apserver.seizure'),
        ),
    ]
