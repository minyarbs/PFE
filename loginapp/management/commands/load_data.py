
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from ...models import AttendanceRecord, Weather, Employee
import pandas as pd
def time_to_float(time_str):
    if pd.isnull(time_str):
        return 0
    else:
        time_parts = time_str.split(':')
        return float(time_parts[0]) + float(time_parts[1]) / 60.0 + float(time_parts[2]) / 3600.0
def delete_data():
    # Load employee information
    employee_df = pd.read_csv("uploads/data/general_info.csv")

    # Load survey data
    survey_df = pd.read_csv("uploads/data/survey.csv")

    # Load attendance data
    attendance_df = pd.read_csv("uploads/data/attendance.csv")
    attendance_df=attendance_df[(attendance_df['Id'] <= 1000)]

    # Merge dataframes
    merged_df = pd.merge(employee_df, survey_df, on='Id')
    merged_df = pd.merge(merged_df, attendance_df, on='Id')
    merged_df=merged_df.dropna()
    

    # Iterate over rows and create AttendanceRecord objects
    for index, row in merged_df.iterrows():
        time_in_str = str(row['time_in'])
        time_out_str = str(row['time_out'])
        try:
         time_in = datetime.strptime(time_in_str, '%H:%M:%S').time() if time_in_str != 'nan' else datetime.strptime('09:00:00', '%H:%M:%S').time()
        except ValueError:
         time_in = None

        try:
         time_out = datetime.strptime(time_out_str, '%H:%M:%S').time() if time_out_str != 'nan' else datetime.strptime('17:00:00', '%H:%M:%S').time()
        except ValueError:
         time_out = None  
        env_sat_str=str(row['EnvironmentSatisfaction'])
        env_sat= int(float(env_sat_str)) if env_sat_str != 'nan' else 0 
        date=datetime.strptime(row['date'], '%Y-%m-%d').date()
        EmployeeId=row['Id']
        existing_objs = AttendanceRecord.objects.filter(date=date,EmployeeId=EmployeeId)
        print(f"objects found for date: {date,EmployeeId}")
        if existing_objs.count()>1:
            print(f"Multiple  objects found for date: {date,EmployeeId}")
            # Keep the first object and delete the rest
            for obj in existing_objs[1:]:
                obj.delete()
def delete_data_id4():
    days = range(1,32)
    months=range(1,13)
    ids=range(1,1001)
    for id in ids:
     for month in months:
      for day in days:
        existing_objs = AttendanceRecord.objects.filter(EmployeeId=id,date__day=day,date__month=month)
        print(f"objects found for date: {day,month,id}")
        if existing_objs.count()>1:
            print(f"Multiple  objects found for date: {day,month,id}")
            # Keep the first object and delete the rest
            for obj in existing_objs[1:]:
                obj.delete()

def load_data():
    # Load employee information
    employee_df = pd.read_csv("uploads/data/general_info.csv")

    # Load survey data
    survey_df = pd.read_csv("uploads/data/survey.csv")

    # Load attendance data
    attendance_df = pd.read_csv("uploads/data/attendance.csv")
    attendance_df=attendance_df[(attendance_df['Id'] <= 1000)]

    # Merge dataframes
    merged_df = pd.merge(employee_df, survey_df, on='Id')
    merged_df = pd.merge(merged_df, attendance_df, on='Id')
    merged_df=merged_df.dropna()
    

    # Iterate over rows and create AttendanceRecord objects
    for index, row in merged_df.iterrows():
        time_in_str = str(row['time_in'])
        time_out_str = str(row['time_out'])
        try:
         time_in = datetime.strptime(time_in_str, '%H:%M:%S').time() if time_in_str != 'nan' else datetime.strptime('09:00:00', '%H:%M:%S').time()
        except ValueError:
         time_in = None

        try:
         time_out = datetime.strptime(time_out_str, '%H:%M:%S').time() if time_out_str != 'nan' else datetime.strptime('17:00:00', '%H:%M:%S').time()
        except ValueError:
         time_out = None  
        env_sat_str=str(row['EnvironmentSatisfaction'])
        env_sat= int(float(env_sat_str)) if env_sat_str != 'nan' else 0 
        date=datetime.strptime(row['date'], '%Y-%m-%d').date()
        EmployeeId=row['Id']
        existing_objs = AttendanceRecord.objects.filter(date=date,EmployeeId=EmployeeId)
        if existing_objs.exists():
            print(f"Multiple Weather objects found for date: {date,EmployeeId}")
            # Keep the first object and delete the rest
            for obj in existing_objs:
                obj.delete()

        AttendanceRecord.objects.get_or_create(
            EmployeeId=row['Id'],
            Age=row['Age'],
            BusinessTravel=row['BusinessTravel'],
            Department=row['Department'],
            DistanceFromHome=row['DistanceFromHome'],
            Gender=row['Gender'],
            JobLevel=row['JobLevel'],
            JobRole=row['JobRole'],
            MaritalStatus=row['MaritalStatus'],
            CompaniesWorked=row['CompaniesWorked'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),  # Convert string to date
            time_in=time_in,  # Convert string to time
            time_out=time_out,  # Convert string to time
            EnvironmentSatisfaction=env_sat,
            JobSatisfaction=row['JobSatisfaction'],
            WorkLifeBalance=row['WorkLifeBalance'],
            MonthlyIncome=row['MonthlyIncome'],
            PercentSalaryHike=row['PercentSalaryHike'],
            is_fraud=False
        )

from django.utils.timezone import make_aware

def load_weather_data():
    weather_df = pd.read_csv("uploads/data/weather.csv")
    
    for index, row in weather_df.iterrows():
        snow_str = str(row['SNOW (Inches)'])
        snow = float(snow_str) if snow_str != 'nan' else 0 

        date = make_aware(datetime.strptime(row['date'], '%Y-%m-%d'))  # Ensure date is timezone-aware
        temperature = row['TAVG (Degrees Fahrenheit)']

        print(f"Processing date: {date}")

        # Check if any Weather objects already exist for this date
        existing_weather_objs = Weather.objects.filter(date=date)
        if existing_weather_objs.exists():
            print(f"Multiple Weather objects found for date: {date}")
            # Keep the first object and delete the rest
            for obj in existing_weather_objs[1:]:
                obj.delete()
            weather_obj = existing_weather_objs.first()
        else:
            # If no objects exist, create a new one
            weather_obj = Weather.objects.create(date=date, temperature=temperature, snow=snow)
            print(f"Created new Weather object for date: {date}")

        # Update fields of the existing or newly created Weather object
        weather_obj.temperature = temperature
        weather_obj.snow = snow
        weather_obj.save()
        print(f"Updated Weather object for date: {date}")

def load_emplyee_names():
   df=pd.read_csv("uploads/data/EmployeeNames.csv", delimiter=";", quotechar='"')
   for index, row in df.iterrows():
      Employee.objects.get_or_create(
         EmployeeId=row['id'],
         Name=row['firstname'],
         LastName=row['lastname'],
         Email=row['email']
      )



class Command(BaseCommand):
    help = 'Load data from csv file'

    def handle(self, *args, **kwargs):
        delete_data_id4()
        