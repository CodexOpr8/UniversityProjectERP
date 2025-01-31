# Imports for managing sales functionality
from django.db import models
from Inventory.models import Store, Product  
from HR.models import Staff
from django.db.models import Sum

class Sales(models.Model):
    # Core sales record attributes
    SalesID = models.AutoField(primary_key=True, unique=True)  # Unique identifier for each sale
    PaymentMethod = models.CharField(max_length=200)  # Method of payment used
    TotalAmount = models.DecimalField(max_digits=15, decimal_places=2)  # Total sale amount
    
    # Foreign key relationships
    StoreID = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')  # Store where sale occurred
    ProductID = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='sales', null=True)  # Product sold
    EmployeeID = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales'
    )  # Staff member who processed the sale
    
    SaleDate = models.DateField(auto_now_add=True)  # Timestamp of sale

    def __str__(self):
        # String representation of sale record
        return f"Id: {self.SalesID} - Total: {self.TotalAmount} - Store: {self.StoreID.StoreName}"

    def GetSalesData(self):
        # ------------------- Returns the sales record data as a dictionary ------------------- 

        # Compile sale details into dictionary format
        return {
            "SalesID": self.SalesID,
            "PaymentMethod": self.PaymentMethod,
            "TotalAmount": self.TotalAmount,
            "Store": self.StoreID.StoreName,
            "Staff": self.EmployeeID.Name if self.EmployeeID else None,
            "SaleDate": self.SaleDate,
        }

    def GetSalesGraph(self, start_date=None, end_date=None):
        # ------------------- 
        #Generates sales data for a graph based on the given date range.
        # start_date: Optional start date for filtering sales (datetime.date).
        # end_date: Optional end date for filtering sales (datetime.date).
        # ------------------- 
        
        # Initialise base queryset
        sales_queryset = Sales.objects.all()

        # Apply date filters if provided
        if start_date:
            sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
        if end_date:
            sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

        # Group sales by date and calculate totals
        sales_summary = (
            sales_queryset
            .values("SaleDate")
            .annotate(TotalSales=Sum("TotalAmount"))
            .order_by("SaleDate")
        )

        return list(sales_summary)  # Returns a list of dictionaries for graph plotting

    def CalculateTotalSales(self, start_date=None, end_date=None):
        # ------------------- 
        # Calculates the total sales amount within the specified date range.
        # start_date: Optional start date for filtering sales (datetime.date).
        # end_date: Optional end date for filtering sales (datetime.date).
        # ------------------- 
        
        # Initialise base queryset
        sales_queryset = Sales.objects.all()

        # Apply date filters if provided
        if start_date:
            sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
        if end_date:
            sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)
        # Calculate total sales amount
        total_sales = sales_queryset.aggregate(TotalSales=Sum("TotalAmount"))
        return total_sales["TotalSales"] or 0
    

    
