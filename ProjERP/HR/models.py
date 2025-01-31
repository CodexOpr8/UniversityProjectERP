# Imports for managing staff data, financial operations and time tracking
from django.db import models
from Finance.models import Department
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta

class Staff(models.Model):
   # Primary staff identifiers and employment details 
   EmployeeID = models.AutoField(primary_key=True, unique=True)
   Name = models.CharField(max_length=200)
   Role = models.CharField(max_length=200)
   Salary = models.IntegerField()
   DepartmentID = models.ForeignKey(
       Department,
       on_delete=models.SET_NULL,
       null=True, 
       blank=True,
       related_name='staff'  # Links staff to department for reverse lookups
   )
   StartDate = models.DateField(auto_now_add=True)

   def __str__(self):
       # Display staff info with department if assigned
       if self.DepartmentID:
           return f"{self.Name} - Role: {self.Role} - In: {self.DepartmentID.DepartmentName}"
       return f"{self.Name} - Role: {self.Role}"

   def GetStaffData(self):
       # Retrieve comprehensive staff member information including department
       return {
           "EmployeeID": self.EmployeeID,
           "Name": self.Name,
           "Role": self.Role,
           "Salary": self.Salary,
           "Department": self.DepartmentID.DepartmentName if self.DepartmentID else None,
           "StartDate": self.StartDate,
       }

   def EditStaffData(self, **kwargs):
       # Update staff information with validation checks
       valid_fields = {'Name', 'Role', 'Salary'}
       
       # Filter kwargs to only allow updates to predefined fields
       update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
       
       if not update_data:
           raise ValueError("No valid fields provided for update")

       # Ensure salary updates are non-negative integers
       if 'Salary' in update_data:
           if not (isinstance(update_data['Salary'], int) and update_data['Salary'] >= 0):
               raise ValueError("Salary must be a non-negative integer.")

       # Dynamically update allowed fields using setattr
       for field, value in update_data.items():
           setattr(self, field, value)

       self.full_clean()  # Run model validation before saving
       self.save()

   def ViewPerformance(self, date_range=30):
       # Calculate staff performance metrics over specified period
       try:
           end_date = datetime.now()
           start_date = end_date - timedelta(days=date_range)

           # Aggregate sales metrics within date range for staff member
           sales_data = Staff.sales.filter(
               EmployeeID=self.EmployeeID,
               SalesDate__range=[start_date, end_date]
           ).aggregate(
               total_sales=Sum('total_amount'),  # Total monetary value of sales
               average_daily_sales=Avg('total_amount'),  # Average sale value per day
               total_transactions=Count('id'),  # Number of sales transactions
           )

           # Calculate derived performance metrics including efficiency ratios
           performance_metrics = {
               "employee_name": self.Name,
               "period_total_sales": sales_data["total_sales"] or 0,
               "average_daily_sales": sales_data["average_daily_sales"] or 0,
               "total_transactions": sales_data["total_transactions"] or 0,
               "sales_per_day": (sales_data["total_sales"] or 0) / date_range,  # Daily sales average
               "performance_index": (sales_data["total_sales"] or 0) / (self.Salary or 1),  # Sales per salary unit
           }

           return performance_metrics

       except Exception as e:  # Handle performance calculation errors
           raise ValueError(f"Error calculating staff performance: {str(e)}")

   def AssignDepartment(self, DepartmentID):
       # Link staff member to department with type validation
       if isinstance(DepartmentID, Department):
           self.DepartmentID = DepartmentID
           self.save()
       else:
           raise ValueError("Invalid department instance.")