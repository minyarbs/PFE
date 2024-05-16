import calendar
from django.test import Client, TestCase
from django.urls import reverse
from .models import Employee, AttendanceRecord 
from django.contrib.auth.models import User
class ViewsTestCase(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(Name='Test Employee', LastName='Test', EmployeeId=5000)
        self.attendance_record = AttendanceRecord.objects.create( EmployeeId=self.employee.EmployeeId, 
                                                                 date='2015-05-11',
                                                                 Age=40, BusinessTravel='text',
                                                                 Department='IT',
                                                                 DistanceFromHome=8,
                                                                 Gender='Female',
                                                                 JobLevel=3,
                                                                 JobRole='HR',
                                                                 MaritalStatus='single',
                                                                 CompaniesWorked=1,
                                                                 time_in='9:30:00',
                                                                 time_out='17:00:00',
                                                                 EnvironmentSatisfaction=5,
                                                                 JobSatisfaction =3,
                                                                 WorkLifeBalance=5,
                                                                 MonthlyIncome=3000,
                                                                 PercentSalaryHike=0,
                                                                 is_fraud=False ,
                                                                 )

        self.client = Client()
        self.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
        

    def test_dashboard_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('dashboard')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loginapp/dashboard.html')

    def test_login_view(self):
        # Test rendering of the login view
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loginapp/login.html')
    
    def test_registration_view(self):
        response = self.client.post(reverse('register'), {'username': 'newuser', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 200)  
    
    def test_logout_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
    
    def test_events_by_date_view(self):
        client = Client()
        # Adjust the URL pattern to match your urls.py
        url = reverse('events_by_date', args=(self.attendance_record.EmployeeId, '05', '11'))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'employeeId')  # Check if the response contains relevant data
        self.assertTemplateUsed(response, 'loginapp/ChangeInstance.html')
    
    def test_update_fraud_status_view(self):
        client = Client()
        url = reverse('update_fraud_status')
        data = {
            'employee_id': self.attendance_record.EmployeeId,
            'selected_month': '05',
            'day': '11',
            'is_fraud': 'true'  
        }
        response = client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        # Check if the fraud status is updated
        updated_record = AttendanceRecord.objects.get(EmployeeId=self.attendance_record.EmployeeId,
                                                      date__month=5, date__day=11)
        self.assertTrue(updated_record.is_fraud)

    def test_charts_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('charts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Percentage of Fraud In the year 2015")
        self.assertContains(response, "<div id=\"chart-container\">")

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class MySeleniumTests(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create a superuser for testing
        self.user = User.objects.create_superuser('myuser', 'myuser@example.com', 'secret')
        # Create sample attendance records
        AttendanceRecord.objects.create(EmployeeId=1, Age=30, BusinessTravel="Travel_Rarely",
                                        Department="Sales", DistanceFromHome=10, Gender="Male",
                                        JobLevel=2, JobRole="Sales Executive", MaritalStatus="Single",
                                        CompaniesWorked=1, date='2015-01-01', time_in='09:00', time_out='17:00',
                                        EnvironmentSatisfaction=3, JobSatisfaction=4, WorkLifeBalance=3,
                                        MonthlyIncome=5000, PercentSalaryHike=10, is_fraud=True)
        AttendanceRecord.objects.create(EmployeeId=2, Age=40, BusinessTravel="Travel_Frequently",
                                        Department="HR", DistanceFromHome=5, Gender="Female",
                                        JobLevel=3, JobRole="HR Manager", MaritalStatus="Married",
                                        CompaniesWorked=2, date='2015-01-02', time_in='08:00', time_out='16:00',
                                        EnvironmentSatisfaction=4, JobSatisfaction=3, WorkLifeBalance=4,
                                        MonthlyIncome=6000, PercentSalaryHike=12, is_fraud=False)

    def test_login_and_charts(self):
        # Log in as the superuser
        self.selenium.get("http://127.0.0.1:8000/login")
        
        # Explicit wait for the login form elements to be present
        WebDriverWait(self.selenium, 60).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("ChesterFriesen")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("Fs%Y59.pd\",@:ML")
        self.selenium.find_element(By.XPATH, '//input[@value="Login"]').click()
        WebDriverWait(self.selenium, 60).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        # Navigate to the charts view
        self.selenium.get("http://127.0.0.1:8000/charts")
        
        # Verify the presence of the chart
        WebDriverWait(self.selenium, 60).until(
            EC.presence_of_element_located((By.ID, "chart-container"))
        )
        
        chart_title = self.selenium.find_element(By.ID, "chart-container")
        self.assertIsNotNone(chart_title)

        # Optionally, you can select a month and check if the chart updates
        month_dropdown = Select(self.selenium.find_element(By.NAME, "month"))
        month_dropdown.select_by_value("1")
        
        # Verify the updated chart
        month_name = calendar.month_name[1]
        WebDriverWait(self.selenium, 50).until(
            EC.presence_of_element_located((By.ID, "chart-container"))
        )
        updated_chart_title = self.selenium.find_element(By.ID, "chart-container")
        self.assertIsNotNone(updated_chart_title)
