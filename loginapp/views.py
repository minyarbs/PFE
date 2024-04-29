import calendar
from django.shortcuts import render,redirect
from . forms import CreateUserForm, FileUploadForm,LoginForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.contrib import messages
from tablib import Dataset
import csv,io
import joblib
import plotly.express as px
from . models import AttendanceRecord, Employee
from django.db.models import Count, F
import plotly.graph_objects as go
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def homepage(request):

    return render(request,'loginapp/index.html')

def register(request):
    form = CreateUserForm()
    if request.method =="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    context={'registerform':form}

    return render(request,'loginapp/register.html',context=context)

def login(request):
    form =LoginForm()
    if request.method=='POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password= password)
            
            if user is not None:
                auth.login(request,user)
                if user.is_superuser:
                    return redirect("dashboard")
                else:
                    return redirect("EmployeeDashboard")
    context={'loginform':form}

    return render(request,'loginapp/login.html',context)

def user_logout(request):
    auth.logout(request)
    return redirect("")

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    form_general_info = FileUploadForm(prefix='general_info')
    form_attendance = FileUploadForm(prefix='attendance')
    form_survey = FileUploadForm(prefix='survey')

    # Read the original files or create empty dataframes if they don't exist yet
    try:
        original_general_info = pd.read_csv("uploads/data/general_info.csv")
    except FileNotFoundError:
        original_general_info = pd.DataFrame(columns=['Id','Age'	,'BusinessTravel'	,'Department',	'DistanceFromHome',	'Gender',	'JobLevel',	'JobRole',	'MaritalStatus',	'CompaniesWorked'
])
    
    try:
        original_attendance = pd.read_csv("uploads/data/attendance.csv")
    except FileNotFoundError:
        original_attendance = pd.DataFrame(columns=['Id', 'date', 'time_in','time_out'])
    
    try:
        survey = pd.read_csv("uploads/data/survey.csv")
    except FileNotFoundError:
        survey = pd.DataFrame(columns=['Id',	'EnvironmentSatisfaction',	'JobSatisfaction',	'WorkLifeBalance'	,'MonthlyIncome',	'PercentSalaryHike'
])

    is_csv_general_info = True
    is_csv_attendance = True
    is_csv_survey=True

    if request.method == 'POST':
        form_general_info = FileUploadForm(request.POST, request.FILES, prefix='general_info')
        form_attendance = FileUploadForm(request.POST, request.FILES, prefix='attendance')
        form_survey = FileUploadForm(request.POST, request.FILES, prefix='survey')
        
        if form_general_info.is_valid():
            uploaded_general_info = form_general_info.save(commit=False)
            file_extension = uploaded_general_info.file.name.split('.')[-1]
            is_csv_general_info = file_extension == 'csv'
            if is_csv_general_info:
                df_general_info = pd.read_csv(uploaded_general_info.file)
                # Concatenate the new data with the original data
                original_general_info = pd.concat([original_general_info, df_general_info], ignore_index=True)
                # Save the combined data back to the file
                original_general_info.to_csv("uploads/data/general_info.csv", index=False)
        if form_survey.is_valid():
            uploaded_survey = form_survey.save(commit=False)
            file_extension = uploaded_survey.file.name.split('.')[-1]
            is_csv_survey = file_extension == 'csv'
            if is_csv_survey:
                df_survey = pd.read_csv(uploaded_survey.file)
                # Concatenate the new data with the original data
                survey = pd.concat([survey, df_survey], ignore_index=True)
                # Save the combined data back to the file
                survey.to_csv("uploads/data/survey.csv", index=False)
                
        if form_attendance.is_valid():
            uploaded_attendance = form_attendance.save(commit=False)
            file_extension = uploaded_attendance.file.name.split('.')[-1]
            is_csv_attendance = file_extension == 'csv'
            if is_csv_attendance:
                df_attendance = pd.read_csv(uploaded_attendance.file)
                # Concatenate the new data with the original data
                original_attendance = pd.concat([original_attendance, df_attendance], ignore_index=True)
                # Save the combined data back to the file
                original_attendance.to_csv("uploads/data/attendance.csv", index=False)

    return render(request, 'loginapp/dashboard.html', {
        'form_general_info': form_general_info,
        'form_attendance': form_attendance,
        'form_survey':form_survey,
        'is_csv_survey':is_csv_survey,
        'csv_content_survey':survey.head(5),
        'is_csv_general_info': is_csv_general_info,
        'is_csv_attendance': is_csv_attendance,
        'csv_content_general_info': original_general_info.head(5),
        'csv_content_attendance': original_attendance.head(5),
    })


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def charts(request):
    selected_month = request.GET.get('month')

    # Filter records based on the selected month
    if selected_month:
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015" 
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date="the year 2015"

    # Load data
    num_fraud = records.filter(is_fraud=True).count()

    # Create a pie chart
    fig = px.pie(
        values=[len(records) - num_fraud, num_fraud], 
        names=["Not Fraud", "Fraud"], 
        title="Percentage of Fraud In " + date,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font= dict(size=15, family="Segoe UI", color="Black"))

    chart= fig.to_html()
        

    return render(request, 'loginapp/charts.html', {
        'chart':chart
    })

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def EmployeeFraud(request):
    selected_month = request.GET.get('month')
    threshold_percentage = request.GET.get('threshold')
    if threshold_percentage:
        threshold_percentage= float(threshold_percentage)
    else:
        threshold_percentage=0.0

    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
        
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date = "the year 2015"
    sum=records.filter(EmployeeId=1).count()
    attendance_records = records.values('EmployeeId').annotate(
     fraud_count=Count('EmployeeId', filter=F('is_fraud')))
    
    employees_above_threshold = attendance_records.filter(fraud_count__gt=threshold_percentage * sum/100)
    if employees_above_threshold:
     employee_ids_above_threshold = employees_above_threshold.values_list('EmployeeId', flat=True)

# Get the employees above the threshold
     employees_object_above_threshold = Employee.objects.filter(id__in=employee_ids_above_threshold)
     names_above_threshold = employees_object_above_threshold.values_list('Name', flat=True)
     last_names=employees_object_above_threshold.values_list('LastName', flat=True)

# Convert the queryset to a DataFrame
     df = pd.DataFrame(employees_above_threshold)
     df['Employee_Name'] =[f"{first} {last}" for first, last in zip(names_above_threshold, last_names)]


# Create a bar chart using Plotly Express
     fig = px.bar(
    df,
    x='Employee_Name',
    y='fraud_count',
    title='Employees with Fraud Count Above '+ str(threshold_percentage) +"% " +"in "+date,
    labels={'Employee_Name': 'Employee Name', 'fraud_count': 'Fraud Count'},
    color_discrete_sequence=px.colors.sequential.Blues_r
)
     fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font=dict(size=15, family="Segoe UI", color="Black"),
                      height=600)

     chart = fig.to_html()
     return render(request, 'loginapp/EmployeeFraud.html', {
        'chart': chart
    })
    else:
        message="No Emplyee surppassed the threshhold "+ str(threshold_percentage)+"%"+" in " + date
        return render(request, 'loginapp/EmployeeFraud.html', {
        'message': message
          })

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def Reasons(request):
    selected_month = request.GET.get('month')
    threshold_percentage = request.GET.get('threshold')
    if threshold_percentage:
        threshold_percentage= float(threshold_percentage)
    else:
        threshold_percentage=0.0

    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date = "the year 2015"
    
    attendance_records = records.values('DistanceFromHome','EmployeeId','BusinessTravel','JobSatisfaction').annotate(
     fraud_count=Count('EmployeeId', filter=F('is_fraud')))
    
    employees_above_threshold = attendance_records.filter(fraud_count__gt=threshold_percentage * Count('EmployeeId')/100)
    if employees_above_threshold:
     
     df = pd.DataFrame(employees_above_threshold)
     df_distance=df.groupby('DistanceFromHome').agg({'fraud_count': 'sum'})
     df_distance = df_distance.reset_index()
     df_travel=df.groupby('BusinessTravel').agg({'fraud_count': 'sum'})
     df_travel = df_travel.reset_index()
     df_sat=df.groupby('JobSatisfaction').agg({'fraud_count': 'sum'})
     df_sat = df_sat.reset_index()

     
# Create a bar chart using Plotly Express
     fig = px.bar(
    df_distance,
    x='DistanceFromHome',
    y='fraud_count',
    title='Distance From Home' ,
    labels={'DistanceFromHome': 'Distance From Home', 'fraud_count': 'Fraud Count'},
    color_discrete_sequence=px.colors.sequential.Blues_r
)
     fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font=dict(size=15, family="Segoe UI", color="Black"),
                      title_x=0.5)

     chart = fig.to_html()
     fig = px.bar(
    df_sat,
    x='JobSatisfaction',
    y='fraud_count',
    title='Job Satisfaction' ,
    labels={'JobSatisfaction': 'Job Satisfaction', 'fraud_count': 'Fraud Count'},
    color_discrete_sequence=px.colors.sequential.Blues_r
)
     fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black",),
                      font=dict(size=15, family="Segoe UI", color="Black"),
                      width=500,
                      title_x=0.5
                      )

     chart3 = fig.to_html()
     labels = df_travel['BusinessTravel'].to_list()
     values = df_travel['fraud_count'].to_list()
     max_index = values.index(max(values))
 
     
# Create a list to hold the pull values for each label
     pull_values = [0] * len(labels)  # Default pull value for all labels
     pull_values[max_index] = 0.2 
     fig = go.Figure(
         data=[go.Pie(labels=labels,
                       values=values, 
                       pull=pull_values,
                       title='Frequency of travels ',
                       
                       )])


     fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font=dict(size=15, family="Segoe UI", color="Black"),
                      title_x=0.5,
                      )
     fig.update_traces(marker=dict(colors=px.colors.sequential.Blues_r))
     chart2 = fig.to_html()
     return render(request, 'loginapp/reasons.html', {
        'chart': chart, 
        'chart2': chart2,
        'title' : 'Fraud Count Above '+ str(threshold_percentage) +"% " +"in "+date,
        'chart3':chart3
    })
    else:
        message="No Emplyee surppassed the threshhold "+ str(threshold_percentage)+"%"+" in " + date
        return render(request, 'loginapp/reasons.html', {
        'message': message,
        'title' : 'Fraud Count Above '+ str(threshold_percentage) +"% " +"in "+date
          })

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def OneEmployee(request):

    selected_month = request.POST.get('month')
   
    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date = "the year 2015"
    if request.method == 'POST':
        FirstName = request.POST.get('FirstName')
        LastName = request.POST.get('LastName')
        if FirstName and LastName:
            try:
                employee_selected = Employee.objects.get(Name=FirstName, LastName=LastName)
                employee_id=employee_selected.EmployeeId
                data=records.filter(EmployeeId=employee_id)
                num_fraud = data.filter(is_fraud=True).count()

    # Create a pie chart
                fig = px.pie(
                    values=[len(data) - num_fraud, num_fraud], 
                    names=["Not Fraud", "Fraud"], 
                    title="Percentage of Fraud In " + date,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                 )
                fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font= dict(size=15, family="Segoe UI", color="Black"))

                chart= fig.to_html()
                return render(request, 'loginapp/one_employee.html', {'chart': chart})
            except ObjectDoesNotExist: # type: ignore
                message = f"No employee with Name: {FirstName} {LastName}"
                return render(request, 'loginapp/one_employee.html', {'message': message})
        else:
            message = "Please enter both First Name and Last Name"
            return render(request, 'loginapp/one_employee.html', {'message': message})
    else:
        message = "Please submit the form to search for an employee"
        return render(request, 'loginapp/one_employee.html', {'message': message})

    
@login_required(login_url="login")
def EmployeeDashboard(request):
    FirstName=request.user.first_name
    LastName=request.user.last_name
    employee=Employee.objects.get(Name=FirstName,LastName=LastName)
    employee_Id=employee.EmployeeId
    Info=AttendanceRecord.objects.get(EmployeeId=employee_Id,date__month=1,date__day=2)
    return render (request, 'loginapp/EmployeeDashboard.html',{
        'first_name':FirstName,
        'last_name':LastName,
        'email':employee.Email,
        'ID':employee_Id,
        'JobRole':Info.JobRole,
        'Department':Info.Department,
        'BusinessTravel':Info.BusinessTravel,
        'CompaniesWorked':Info.CompaniesWorked
    })
@login_required(login_url="login")
def FraudView(request):
    FirstName=request.user.first_name
    LastName=request.user.last_name
    employee=Employee.objects.get(Name=FirstName,LastName=LastName)
    employee_Id=employee.EmployeeId
    selected_month = request.GET.get('month')
   
    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
        
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.filter(date__month=12)
        date = "the month of December 2015"
    
    Info=records.filter(EmployeeId=employee_Id,is_fraud=True)
    count_all=records.filter(EmployeeId=employee_Id).count()
    pourcentage=Info.count()/count_all*100
    return render (request, 'loginapp/FraudView.html',{
        'first_name':FirstName,
        'last_name':LastName,
        'ID':employee_Id,
        'Info':Info,
        'pourcentage':pourcentage,
        'date':date
    })