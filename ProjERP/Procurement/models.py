# Imports for managing supplier data, purchase orders and time operations
from django.db import models
from Inventory.models import Product
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta

class Supplier(models.Model):
   # Primary supplier identifiers and contact information
   SupplierID = models.AutoField(primary_key=True, unique=True)
   SupplierName = models.CharField(max_length=200)
   ContactDetails = models.CharField(max_length=200)
   Location = models.CharField(max_length=200)
   ContractTerms = models.CharField(max_length=200)

   def __str__(self):
       return f"{self.SupplierName} - {self.Location}"

   def GetSupplierProducts(self):
       # Get all products supplied by this supplier using SupplierID relationship
       return Product.objects.filter(SupplierID=self.SupplierID)

   def SetSupplierData(self, **kwargs):
       # Update supplier details with field validation against allowed list
       allowed_fields = {"SupplierName", "ContactDetails", "Location", "ContractTerms"}
       for field, value in kwargs.items():
           if field not in allowed_fields:
               raise ValueError(f"Invalid field: {field}")
           setattr(self, field, value)  # Dynamically set field values using setattr
       self.save()

   def ViewSupplierPerformance(self, dateRange=30):
       # Calculate supplier performance metrics within specified date window 
       endDate = datetime.now()
       startDate = endDate - timedelta(days=dateRange)

       # Filter orders by supplier, delivery date and completed status
       orders = PurchaseOrder.objects.filter(
           ProductId__SupplierId=self.SupplierID,  # Filter through product to supplier
           DeliveryDate__range=[startDate, endDate],  # Date range filter using __range
           OrderStatus="Delivered",
       )

       # Calculate totals with null handling for empty result sets
       totalAmount = orders.aggregate(total=Sum("TotalAmount"))["total"] or 0
       totalOrders = orders.count()

       # Compute performance metrics with division by zero protection
       performance = {
           "TotalDeliveredOrders": totalOrders,
           "TotalDeliveredAmount": totalAmount,
           "AverageOrderValue": totalAmount / totalOrders if totalOrders > 0 else 0,
       }
       return performance

class PurchaseOrder(models.Model):
   # Primary purchase order details with automatic ID generation
   PurchaseOrderID = models.AutoField(primary_key=True, unique=True)
   TotalAmount = models.DecimalField(max_digits=10, decimal_places=2)
   ProductID = models.ForeignKey(Product, on_delete=models.CASCADE)  # Links to product with cascade delete
   OrderDate = models.DateField(auto_now_add=True)  # Automatically set on creation
   DeliveryDate = models.DateField(blank=True, null=True)  # Optional expected delivery date
   OrderStatus = models.CharField(max_length=200)

   def __str__(self):
       return f"Id:{self.PurchaseOrderID} - Contains:{self.ProductID.ProductName} - Amount:{self.TotalAmount} - Status:{self.OrderStatus}"

   @classmethod
   def CreatePurchaseOrder(cls, product, totalAmount, deliveryDate, orderStatus="Pending"):
       # Factory method to create new purchase orders with status defaulting to Pending
       return cls.objects.create(
           ProductID=product,
           TotalAmount=totalAmount,
           DeliveryDate=deliveryDate,
           OrderStatus=orderStatus,
       )

   def GetPurchaseOrderStatus(self):
       # Get current status string for order tracking
       return self.OrderStatus

   def SetPurchaseOrder(self, **kwargs):
       # Update order details with validation against permitted fields
       allowed_fields = {"TotalAmount", "DeliveryDate", "OrderStatus"}
       for field, value in kwargs.items():
           if field not in allowed_fields:
               raise ValueError(f"Invalid field: {field}")
           setattr(self, field, value)  # Dynamic field updates using setattr
       self.save()