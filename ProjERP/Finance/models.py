# Imports for managing data model and business transactions
from django.db import models

class Department(models.Model):
    # Primary database identifiers and descriptive fields
    DepartmentID = models.AutoField(primary_key=True, unique=True)
    DepartmentName = models.CharField(max_length=200)
    ManagerID = models.OneToOneField(
        "HR.Staff", on_delete=models.SET_NULL, null=True, blank=True, related_name="department"
    )
    Budget = models.IntegerField()

    def __str__(self):
        # Display department info with manager name if available
        if self.ManagerID:
            return f"{self.DepartmentName} - Manager: {self.ManagerID.Name}"
        return f"{self.DepartmentName}"
    
    def GetDepartmentEmployees(self):
        # Retrieve all staff members linked to this department
        return self.staff.all()
    
    def GetDepartmentBudget(self):
        # Simple getter for department budget allocation
        return self.Budget

    def SetDepartmentBudget(self, budget):
        # Validate and update department budget with safeguards
        if isinstance(budget, int) and budget >= 0:
            self.Budget = budget
            self.save()
        else:
            raise ValueError("Budget must be a non-negative integer.")

