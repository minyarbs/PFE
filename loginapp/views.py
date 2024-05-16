import calendar
from django.shortcuts import render,redirect
from . forms import CreateUserForm, FileUploadForm,LoginForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly.express as px
from . models import AttendanceRecord, Employee
from django.db.models import Count, F
import plotly.graph_objects as go
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test
import calendar
from calendar import HTMLCalendar
from bs4 import BeautifulSoup
from django.http import JsonResponse


# Create your views here.
def homepage(request):

    return render(request,'loginapp/index.html' )

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
    message=''
    message2=''
    message3=''
    message_succ=''

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
                expected_fields = ['Id','Age','BusinessTravel','Department','DistanceFromHome','Gender','JobLevel','JobRole','MaritalStatus','CompaniesWorked']  # Replace with your field names
                missing_fields = [field for field in expected_fields if field not in df_general_info.columns]
                if missing_fields:
                    message= "The following fields are missing:", missing_fields
                else:
                    original_general_info = pd.concat([original_general_info, df_general_info], ignore_index=True)
                    original_general_info = original_general_info.drop_duplicates()
                    original_general_info.to_csv("uploads/data/general_info.csv", index=False)
                    message_succ="Upload Was successful"
            else:
                message= "Uploaded file is not a CSV."

        if form_survey.is_valid():
            uploaded_survey = form_survey.save(commit=False)
            file_extension = uploaded_survey.file.name.split('.')[-1]
            is_csv_survey = file_extension == 'csv'
            if is_csv_survey:
                df_survey = pd.read_csv(uploaded_survey.file)
                expected_fields = ['Id','EnvironmentSatisfaction','JobSatisfaction','WorkLifeBalance','MonthlyIncome','PercentSalaryHike']  # Replace with your field names
                missing_fields = [field for field in expected_fields if field not in df_survey.columns]
                if missing_fields:
                    message2= "The following fields are missing:", missing_fields
                else:
                 survey = pd.concat([survey, df_survey], ignore_index=True)
                 survey = survey.drop_duplicates()
                # Save the combined data back to the file
                 survey.to_csv("uploads/data/survey.csv", index=False)
            else:
                message2="Uploaded file is not a CSV." 
        if form_attendance.is_valid():
            uploaded_attendance = form_attendance.save(commit=False)
            file_extension = uploaded_attendance.file.name.split('.')[-1]
            is_csv_attendance = file_extension == 'csv'
            if is_csv_attendance:
                df_attendance = pd.read_csv(uploaded_attendance.file)
                expected_fields = ['Id','date','time_in','time_out']  # Replace with your field names
                missing_fields = [field for field in expected_fields if field not in df_attendance.columns]
                if missing_fields:
                    message3= "The following fields are missing:", missing_fields
                else:
                # Concatenate the new data with the original data
                 original_attendance = pd.concat([original_attendance, df_attendance], ignore_index=True)
                 original_general_info =original_general_info.drop_duplicates()
                 original_attendance.to_csv("uploads/data/attendance.csv", index=False)
            else:
                message3="The uploaded file is not a csv"
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
        'message':message,
        'message3':message3,
        'message2':message2,
        'message_succ':message_succ

    })


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def charts(request):
    selected_month = request.POST.get('month')

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
        'chart':chart,
        'selected_month':str(selected_month)
    })

@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def EmployeeFraud(request):
    selected_month = request.GET.get('month')
    threshold_percentage = request.GET.get('threshold')

    # Convert threshold_percentage to float if it exists
    threshold_percentage = float(threshold_percentage) if threshold_percentage else 0.0

    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date = "the year 2015"

    

    # Get the sum of records for a specific EmployeeId (change EmployeeId=1 to the desired EmployeeId)
    sum_records_employee = records.filter(EmployeeId=1).count()

    # Annotate the queryset to get the fraud count for each EmployeeId
    attendance_records = records.values('EmployeeId').annotate(
        fraud_count=Count('EmployeeId', filter=F('is_fraud'))
    )

    # Filter employees with fraud count above the threshold
    employees_above_threshold = attendance_records.filter(fraud_count__gt=threshold_percentage * sum_records_employee / 100)

    if employees_above_threshold:
        # Get the EmployeeIds above the threshold
        employee_ids_above_threshold = employees_above_threshold.values_list('EmployeeId', flat=True)

        # Get Employee objects for the above-threshold EmployeeIds
        employees_object_above_threshold = Employee.objects.filter(id__in=employee_ids_above_threshold)

        # Get names and last names of employees above threshold
        names_above_threshold = employees_object_above_threshold.values_list('Name', flat=True)
        last_names = employees_object_above_threshold.values_list('LastName', flat=True)

        # Create a DataFrame from the queryset
        df = pd.DataFrame(employees_above_threshold)
        df['Employee_Name'] = [f"{first} {last}" for first, last in zip(names_above_threshold, last_names)]

        # Create a bar chart using Plotly Express
        fig = px.bar(
            df,
            x='Employee_Name',
            y='fraud_count',
            title='Employees with Fraud Count Above ' + str(threshold_percentage) + "% " + "in " + date,
            labels={'Employee_Name': 'Employee Name', 'fraud_count': 'Fraud Count'},
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(
            title_font=dict(size=20, family="Segoe UI", color="Black"),
            font=dict(size=15, family="Segoe UI", color="Black"),
            height=600
        )

        chart = fig.to_html()
        return render(request, 'loginapp/EmployeeFraud.html', {
            'chart': chart,
            'selected_month': str(selected_month),  # Pass the selected month back to the template
            'threshold_percentage': threshold_percentage  # Pass the threshold percentage back to the template
        })
    else:
        message = "No Employee surpassed the threshold " + str(threshold_percentage) + "%" + " in " + date
        return render(request, 'loginapp/EmployeeFraud.html', {
            'message': message,
            'selected_month': str(selected_month),  # Pass the selected month back to the template
            'threshold_percentage': threshold_percentage  # Pass the threshold percentage back to the template
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
    
    sum_records_employee = records.filter(EmployeeId=1).count()
    
    employees_above_threshold = attendance_records.filter(fraud_count__gt=threshold_percentage * sum_records_employee/100)
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
        'chart3':chart3,
        'selected_month': selected_month, 
    })
    else:
        message="No Employee surppassed the threshhold "+ str(threshold_percentage)+"%"+" in " + date
        return render(request, 'loginapp/reasons.html', {
        'message': message,
        'selected_month': selected_month, 
        'title' : 'Fraud Count Above '+ str(threshold_percentage) +"% " +"in "+date
          })


@login_required(login_url="login")
@user_passes_test(lambda u: u.is_superuser)
def OneEmployee(request):

    selected_month = request.GET.get('month')
        # Inside your view function
    initial_first_name = request.GET.get('initial_first_name', '') 
    initial_last_name = request.GET.get('initial_last_name', '') 
    if request.method == 'POST':
        FirstName = request.POST.get('FirstName')
        LastName = request.POST.get('LastName')
    else:
        FirstName = initial_first_name
        LastName = initial_last_name
    print(FirstName,LastName)
   
    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        records = AttendanceRecord.objects.filter(date__month=selected_month)
        month_name = calendar.month_name[int(selected_month)]
        date = f"the month of {month_name} 2015"
    else:
        # If no month is selected, fetch all records
        records = AttendanceRecord.objects.all()
        date = "the year 2015"
 
    if FirstName and LastName:
            try:
                employee_selected = Employee.objects.get(Name=FirstName, LastName=LastName)
                employee_id=employee_selected.EmployeeId
                data=records.filter(EmployeeId=employee_id)
                num_fraud = data.filter(is_fraud=True).count()
                fig = px.pie(
                    values=[len(data) - num_fraud, num_fraud], 
                    names=["Not Fraud", "Fraud"], 
                    title="Percentage of Fraud In " + date,
                    color_discrete_sequence=px.colors.sequential.Sunset
                 )
                fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font= dict(size=15, family="Segoe UI", color="Black"))

                chart= fig.to_html()
                if selected_month and selected_month != "Select Month":
                 cal_html = HTMLCalendar().formatmonth(
                    2015,
                    int(selected_month) )
                 soup = BeautifulSoup(cal_html, 'html.parser')
                 date_cells = soup.find_all('td')
                 for cell in date_cells:
                    day = cell.text.strip()
                    if day.isdigit():
                        day = int(day)
                        
                        try:
                            check_fraud= AttendanceRecord.objects.get(EmployeeId=employee_id,date__month=selected_month,date__day=str(day)).is_fraud
                            cell_link = f'/{employee_id}/2015-{selected_month}-{day}'
                            cell.clear()  # Adjust the URL pattern as needed
                            new_anchor = soup.new_tag('a', href=cell_link)
                            new_anchor.string = str(day)
                            cell.append(new_anchor)
                        except:
                            check_fraud=False
                        if check_fraud:
                            cell['class'] = 'fraud' 
                             
                 cal_html_with_classes = str(soup)
                 return render(request, 'loginapp/one_employee.html', {'chart': chart, 'selected_month': selected_month,'initial_first_name': FirstName,'initial_last_name': LastName, 'cal': cal_html_with_classes})
                else:
                    return render(request, 'loginapp/one_employee.html', {'chart': chart, 'selected_month': selected_month,'initial_first_name': FirstName,'initial_last_name': LastName})
            except ObjectDoesNotExist: # type: ignore
                message = f"No employee with Name: {FirstName} {LastName}"
                return render(request, 'loginapp/one_employee.html', {'message': message, 
                                                                      'selected_month': selected_month,
                                                                      'initial_first_name': FirstName,
                                                                      'initial_last_name': LastName,})
    else:
            message = "Please enter both First Name and Last Name"
            return render(request, 'loginapp/one_employee.html', {'message': message, 
                                                                      'selected_month': selected_month,
                                                                      'initial_first_name': FirstName,
                                                                      'initial_last_name': LastName,})
  
@login_required(login_url="login")
def AccountInfo(request):
    FirstName=request.user.first_name
    LastName=request.user.last_name
    employee=Employee.objects.get(Name=FirstName,LastName=LastName)
    employee_Id=employee.EmployeeId
    Info=AttendanceRecord.objects.get(EmployeeId=employee_Id,date__month=1,date__day=2)
    return render (request, 'loginapp/AccountInfo.html',{
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
    FirstName = request.user.first_name
    LastName = request.user.last_name
    employee = Employee.objects.get(Name=FirstName, LastName=LastName)
    employee_Id = employee.EmployeeId
    selected_month = request.GET.get('month')

    # Filter records based on the selected month
    if selected_month and selected_month != "Select Month":
        selected_month = int(selected_month)
        records = AttendanceRecord.objects.filter(EmployeeId=employee_Id,date__month=selected_month)
        month_name = calendar.month_name[selected_month]
        date = f"the month of {month_name} 2015"

    else:
        # If no month is selected, default to December
        selected_month = 12
        records = AttendanceRecord.objects.filter(EmployeeId=employee_Id,date__month=12)
        date = "the month of December 2015"

    cal_html = HTMLCalendar().formatmonth(
        2015,
        selected_month
    )

    soup = BeautifulSoup(cal_html, 'html.parser')
    date_cells = soup.find_all('td')
    for cell in date_cells:
     day = cell.text.strip()
     if day.isdigit():
        day = int(day)
        try:
            check_fraud= AttendanceRecord.objects.get(EmployeeId=employee_Id,date__month=selected_month,date__day=str(day)).is_fraud
        except:
            check_fraud=False
        # Check if this date has fraud (you need to implement this logic)
        if check_fraud:
            cell['class'] = 'fraud'  # Add 'fraud' class to highlight the date

# Convert the modified BeautifulSoup object back to HTML string
    cal_html_with_classes = str(soup)
    print(selected_month)
    return render(request, 'loginapp/FraudView.html', {
        
        'cal': cal_html_with_classes, 'selected_month':str(selected_month)
    })

@login_required(login_url="login")
def EmployeeDashboard(request):
    FirstName=request.user.first_name
    LastName=request.user.last_name
    employee=Employee.objects.get(Name=FirstName,LastName=LastName)
    employee_Id=employee.EmployeeId
    Info=AttendanceRecord.objects.filter(EmployeeId=employee_Id)
    selected_month = request.GET.get('month')
    # Filter records based on the selected month
    if selected_month == None:
        selected_month=12
        
    records = AttendanceRecord.objects.filter(EmployeeId=employee_Id,date__month=selected_month)
    month_name = calendar.month_name[int(selected_month)]
    date = f"the month of {month_name} 2015"
    num_fraud = records.filter(is_fraud=True).count()
    fig = px.pie(
                    values=[len(records) - num_fraud, num_fraud], 
                    names=["Not Fraud", "Fraud"], 
                    title="Your Percentage of Fraud In " + date,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                 )
    fig.update_layout(title_font=dict(size=20, family="Segoe UI", color="Black"),
                      font= dict(size=15, family="Segoe UI", color="Black"))

    chart= fig.to_html()
    percentage=num_fraud*100/len(records)        
    return render(request, 'loginapp/EmployeeDashboard.html',{
        'first_name':FirstName,
        'last_name': LastName,
        'chart':chart,
        'selected_month':str(selected_month),
        'percentage':percentage
    })

@login_required(login_url="login")
def AboutCompany (request):
    return render(request, 'loginapp/AboutCompany.html')

def AboutITServ (request):
    return render(request, 'loginapp/AboutITSERV.html')


from django.shortcuts import render

def events_by_date(request, employeeId,selected_month, day):
    employee=Employee.objects.get(EmployeeId=employeeId)
    Attendancerecord=AttendanceRecord.objects.get(EmployeeId=employeeId,date__month=selected_month,date__day=day)
    
    return render(request, 'loginapp/ChangeInstance.html', {
        'employee': employee, 
        'month': selected_month,
        'day':day,
        'attendance':Attendancerecord
        })

def update_fraud_status(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee_id = request.POST.get('employee_id')
        selected_month = request.POST.get('selected_month')
        day = request.POST.get('day')
        is_fraud = request.POST.get('is_fraud') == 'true'  # Convert string to boolean
        try:
            record = AttendanceRecord.objects.get(EmployeeId=employee_id, date__month=selected_month, date__day=day)
            record.is_fraud = is_fraud
            record.save()
            return JsonResponse({'success': True})
        except AttendanceRecord.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Record not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
