from loginapp.models import Weather, AttendanceRecord,Employee

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load data from csv file'

    def handle(self, *args, **kwargs):
        
# Count the number of Weather instances
        weather_count = Employee.objects.all().count()

# Alternatively, you can retrieve all instances and use len() to get the count
# weather_instances = Weather.objects.all()
# weather_count = len(weather_instances)

        print(f"Number of Weather instances: {weather_count}")
