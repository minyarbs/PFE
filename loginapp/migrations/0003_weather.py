# Generated by Django 4.2.11 on 2024-04-15 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0002_attendancerecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('temperture', models.FloatField()),
                ('snow', models.FloatField()),
            ],
            options={
                'ordering': ('date',),
            },
        ),
    ]