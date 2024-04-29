from django.core.management.base import BaseCommand
import joblib
import pandas as pd
import numpy as np
from loginapp.models import AttendanceRecord

def update_outliers():
    data = pd.read_csv("uploads/data/reduced_data.csv")
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data=data[(data['Id'] <= 1000)]

    # Load the Isolation Forest model
    isolation_model = joblib.load("uploads/models/autoencoder.pkl")

    # Predict outliers
    predictions = isolation_model.predict(data)
    reconstruction_errors = np.mean(np.square(data - predictions), axis=1)
    threshold = np.mean(reconstruction_errors) + 2 * np.std(reconstruction_errors)
    data['is_outlier'] = reconstruction_errors > threshold

    # Update 'is_outlier' field for existing Attendancerecord instances
    for index, row in data.iterrows():
        try:
            record = AttendanceRecord.objects.get(date=index,EmployeeId=row['Id'])
            print('attendance record found',index,row['Id'])
            record.is_fraud= row['is_outlier']  # Assuming predictions is a dictionary
            record.save()
        except AttendanceRecord.DoesNotExist:
            # Handle case where record does not exist for the given date
            print(f"No Attendance record found for date: {index}")
class Command(BaseCommand):
    help = 'Update Outliers'

    def handle(self, *args, **kwargs):
        update_outliers()