# invoices/urls.py
from django.urls import path
from .views import InvoiceListCreateView, InvoiceDetailView, InvoicePDFView, EmailInvoiceView


urlpatterns = [
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/pdf/', InvoicePDFView.as_view(), name='invoice-pdf'),
    path('invoices/<int:pk>/email/', EmailInvoiceView.as_view(), name='invoice-email'),
]

