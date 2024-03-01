# Generated by Django 5.0.2 on 2024-02-29 18:23

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
                ('ip', models.CharField(max_length=32, unique=True)),
                ('area', models.CharField(max_length=64, unique=True)),
                ('is_online', models.BooleanField(default=True)),
                ('is_attacking', models.BooleanField(default=False)),
                ('last_heartbeat', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='InfoHistory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('user_type', models.CharField(blank=True, max_length=64)),
                ('user_info', models.TextField(blank=True)),
                ('capture_time', models.DateTimeField(auto_now_add=True)),
                ('area', models.CharField(max_length=64)),
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
                ('info_history', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='apscavenge.infohistory')),
            ],
        ),
        migrations.AddField(
            model_name='infohistory',
            name='seizure_email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apscavenge.seizure'),
        ),
    ]
