from django.db import models

from django.contrib.auth.models import AbstractUser

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')

class AttendanceRecord(models.Model):
    EmployeeId= models.PositiveIntegerField()
    Age	=models.PositiveIntegerField()
    BusinessTravel=models.CharField(max_length=50)
    Department=models.CharField(max_length=50)
    DistanceFromHome=models.PositiveIntegerField()
    Gender=models.CharField(max_length=50)
    JobLevel=models.PositiveIntegerField()
    JobRole=models.CharField(max_length=50)
    MaritalStatus=models.CharField(max_length=50)
    CompaniesWorked=models.PositiveIntegerField()
    date=models.DateField()
    time_in=models.TimeField()
    time_out=models.TimeField()
    EnvironmentSatisfaction=models.PositiveIntegerField()
    JobSatisfaction	=models.PositiveIntegerField()
    WorkLifeBalance=models.PositiveIntegerField()
    MonthlyIncome=models.PositiveIntegerField()
    PercentSalaryHike=models.PositiveIntegerField()
    is_fraud=models.BooleanField()
    class Meta:
       ordering=('date','EmployeeId')
class Weather(models.Model):
    date=models.DateField()
    temperture=models.FloatField()
    snow=models.FloatField()
    class Meta:
        ordering=('date',)
class Employee(models.Model):
    EmployeeId=models.PositiveIntegerField()
    Name=models.CharField(max_length=50)
    LastName=models.CharField(max_length=50)
    Email=models.CharField(max_length=255)

