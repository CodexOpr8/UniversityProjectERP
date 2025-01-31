# Imports for managing inventory, store locations and validation operations
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg
from datetime import datetime, timedelta

class Product(models.Model):
   # Primary product identifiers and inventory tracking fields
   ProductID = models.AutoField(primary_key=True, unique=True)
   ProductName = models.CharField(max_length=200)
   Category = models.CharField(max_length=100)
   Price = models.DecimalField(max_digits=10, decimal_places=2)
   StockLevel = models.IntegerField()
   ReorderQuantity = models.IntegerField()
   LastPurchaseDate = models.DateField(null=True, blank=True)
   SupplierID = models.ForeignKey(
       "Procurement.Supplier",
       null=True,
       related_name="products",  # Links products back to supplier
       on_delete=models.SET_NULL,
   )

   def __str__(self):
       # Display product info with stock levels
       return f"{self.ProductName} - Level:{self.StockLevel} Order at:{self.ReorderQuantity}"

   def GetAllStores(self):
       # Get store locations stocking this product
       return self.stocklocation_set.values("StoreId__StoreName", "StoreId__Location")

   def GetStockLevel(self):
       # Calculate total stock across all store locations
       return self.stocklocation_set.aggregate(TotalStock=Sum("Quantity"))["TotalStock"] or 0

   def TransferStock(self, from_store, to_store, quantity):
       # Handle inter-store stock transfers with validation
       if quantity <= 0:
           raise ValueError("Quantity must be greater than zero.")

       # Check source and destination stock levels
       from_stock = self.stocklocation.filter(StoreId=from_store).first()
       to_stock = self.stocklocation.filter(StoreId=to_store).first()

       if not from_stock or from_stock.Quantity < quantity:
           raise ValidationError("Insufficient stock in the source store.")

       # Update stock levels for both locations
       from_stock.Quantity -= quantity
       from_stock.save()

       if to_stock:
           to_stock.Quantity += quantity
       else:
           # Create new stock location if product not stocked at destination
           ProductLocation.objects.create(ProductID=self, StoreId=to_store, Quantity=quantity)
       to_stock.save()

   def EditReorderLevel(self, new_reorder_level):
       # Update product reorder threshold with validation
       if new_reorder_level < 0:
           raise ValueError("Reorder level must be a non-negative integer.")
       self.ReorderQuantity = new_reorder_level
       self.save()

class Store(models.Model):
   # Primary store identifiers and operational details
   StoreId = models.AutoField(primary_key=True, unique=True)
   StoreName = models.CharField(max_length=200)
   Location = models.CharField(max_length=200)
   ContactNumber = models.CharField(max_length=15)
   ManagerId = models.OneToOneField(
       "HR.Staff",
       null=True,
       on_delete=models.SET_NULL,
   )
   TotalSales = models.IntegerField()
   OperatingHours = models.IntegerField()

   def __str__(self):
       return f"{self.StoreName} - {self.Location}"

   def GetAllProducts(self):
       # Retrieve current product inventory for store
       return self.stocklocation_set.values("ProductId__ProductName", "Quantity")

   def ViewStorePerformance(self):
       # Calculate store performance metrics including hourly sales
       return {
           "TotalSales": self.TotalSales,
           "AverageSalesPerHour": (self.TotalSales / self.OperatingHours if self.OperatingHours else 0),
       }

   def edit_store_data(self, **kwargs):
       # Update store information with comprehensive validation
       try:
           # Define fields that can be safely updated
           valid_fields = {"StoreName", "Location", "ContactNumber", "ManagerId", "OperatingHours"}
           update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
           
           if not update_data:
               raise ValidationError("No valid fields provided for update")

           # Validate phone number format if updating
           if "ContactNumber" in update_data:
               if not update_data["ContactNumber"].replace("+", "").isdigit():
                   raise ValidationError("Invalid contact number format")

           # Ensure operating hours are within valid range
           if "OperatingHours" in update_data:
               if not 0 < update_data["OperatingHours"] <= 24:
                   raise ValidationError("Operating hours must be between 1 and 24")

           # Apply updates using dynamic field assignment
           for field, value in update_data.items():
               setattr(self, field, value)
           self.full_clean()  # Validate all model fields
           self.save()
           return True

       except ValidationError as ve:  # Handle validation specific errors
           raise ValidationError(f"Validation error: {str(ve)}")
       except Exception as e:  # Handle unexpected errors
           raise ValueError(f"Error updating store data: {str(e)}")

class ProductLocation(models.Model):
   # Junction model tracking product quantities at each store
   ProductLocationID = models.AutoField(primary_key=True, unique=True)
   ProductID = models.ForeignKey(
       Product, on_delete=models.CASCADE, related_name="stocklocation"
   )
   StoreId = models.ForeignKey(
       Store, on_delete=models.CASCADE, related_name="stocklocation"
   )
   Quantity = models.IntegerField()
   Date = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return f"{self.ProductID.ProductName} - {self.StoreId.StoreName} - Amount: {self.Quantity}"

   def AdjustStock(self, quantity):
       # Update stock levels with understock prevention 
       if self.Quantity + quantity < 0:
           raise ValidationError("Insufficient stock for the operation.")
       self.Quantity += quantity
       self.save()