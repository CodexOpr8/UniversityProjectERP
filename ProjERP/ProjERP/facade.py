# Imports for managing inventory, procurement, and sales functionality
from Inventory import Product
from Procurement import Supplier, PurchaseOrder
from Sales.models import Sales
from Inventory.models import Product, Store

class Facade:  # Facade pattern to simplify complex subsystem interactions
    def __init__(self):
        # Initialise with all records from core business models
        self.sales = Sales.objects.all()    # All sales records
        self.stores = Store.objects.all()   # All store locations  
        self.products = Product.objects.all()   # All product inventory


    def GetSalesPerformance(self, start_date=None, end_date=None):
        try:
            from django.db.models import Sum  # Import for aggregation operations

            sales_queryset = self.sales
            if start_date:  # Apply date filters if provided
                sales_queryset = sales_queryset.filter(DateOfSale__gte=start_date)
            if end_date:
                sales_queryset = sales_queryset.filter(DateOfSale__lte=end_date)

            # Group sales by store and calculate totals
            store_sales = (
                sales_queryset.values("StoreID__StoreName")
                .annotate(TotalSales=Sum("TotalAmount"))
                .order_by("StoreId__StoreName")
            )

            # Group sales by store and product with totals
            product_sales = (
                sales_queryset.values("StoreId__StoreName", "ProductID__ProductName")
                .annotate(TotalSales=Sum("TotalAmount"))
                .order_by("ProductID__ProductName")
            )

            return {"store_sales": list(store_sales), "product_sales": list(product_sales)}

        except Exception as e:  # Handle aggregation errors
            raise ValueError(f"Error generating sales performance graph: {str(e)}")

    def TriggerPurchaseOrder(self, productId):
        try:
            product = Product.objects.get(ProductId=productId)  # Get product details
            currentStock = product.GetStockLevel()  # Check current inventory level

            if currentStock < product.ReorderLevel:  # Stock below threshold
                supplier = Supplier.objects.get(SupplierID=product.SupplierID.SupplierID)  # Get product supplier

                if not supplier.exists():  # Validate supplier existence
                    return f"No supplier found for product ID {productId}."

                reorderQuantity = product.ReorderLevel - currentStock  # Calculate needed quantity
                totalAmount = reorderQuantity * product.Price  # Calculate order cost

                # Create PO with necessary details
                purchaseOrder = PurchaseOrder.CreatePurchaseOrder(
                    product=product,
                    totalAmount=totalAmount,
                    orderStatus="Pending",
                    SupplierID=supplier
                )

                return f"Purchase order {purchaseOrder.PurchaseOrderID} created for product ID {productId} with quantity {reorderQuantity}."
            else:
                return f"Stock level ({currentStock}) for product ID {productId} is sufficient. No purchase order needed."

        except Product.DoesNotExist:  # Handle invalid product ID
            return f"Product ID {productId} does not exist."
        except Exception as e:  # Catch other potential errors
            return f"Error triggering purchase order: {str(e)}"

