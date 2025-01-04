# invoices/models.py
from django.db import models
from django.conf import settings

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    date = models.DateField()
    payment_terms = models.CharField(max_length=255)
    due_date = models.DateField()
    po_number = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)  # Optional field for logo
    sender = models.CharField(max_length=255, default="Sender Name")  # Default value for sender
    notes = models.TextField(null=True, blank=True, default="") # notes just added
    customer_name = models.CharField(max_length=255, default="Customer Name")  # Default value for customer_name
    # subtotal = models.DecimalField(max_digits=10, decimal_places=2) # dynamically calculated
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    shipment = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return sum(item.amount for item in self.items.all())

    @property
    def total(self):
        return self.subtotal + self.tax + self.shipment - self.discount


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

