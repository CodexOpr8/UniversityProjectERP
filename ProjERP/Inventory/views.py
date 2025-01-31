from django.http import JsonResponse
from django.shortcuts import render

from app.facade import Facade


def SalesPerformanceGraphView(request):
    facade = Facade()
    start_date = request.GET.get("start_date")  # Optional date from query parameters
    end_date = request.GET.get("end_date")

    sales_data = facade.GetSalesPerformanceGraph(start_date, end_date)

    return JsonResponse(
        {
            "store_sales": sales_data["store_sales"],
            "product_sales": sales_data["product_sales"],
        }
    )
