# Generated by Django 4.2.11 on 2024-04-15 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EmployeeId', models.PositiveIntegerField()),
                ('Age', models.PositiveIntegerField()),
                ('BusinessTravel', models.CharField(max_length=50)),
                ('Department', models.CharField(max_length=50)),
                ('DistanceFromHome', models.PositiveIntegerField()),
                ('Gender', models.CharField(max_length=50)),
                ('JobLevel', models.PositiveIntegerField()),
                ('JobRole', models.CharField(max_length=50)),
                ('MaritalStatus', models.CharField(max_length=50)),
                ('CompaniesWorked', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('time_in', models.TimeField()),
                ('time_out', models.TimeField()),
                ('EnvironmentSatisfaction', models.PositiveIntegerField()),
                ('JobSatisfaction', models.PositiveIntegerField()),
                ('WorkLifeBalance', models.PositiveIntegerField()),
                ('MonthlyIncome', models.PositiveIntegerField()),
                ('PercentSalaryHike', models.PositiveIntegerField()),
                ('is_fraud', models.BooleanField()),
            ],
            options={
                'ordering': ('date', 'EmployeeId'),
            },
        ),
    ]