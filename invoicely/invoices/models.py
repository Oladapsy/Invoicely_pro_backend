# invoices/models.py
from django.db import models
from django.conf import settings

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, null=True)
    date = models.DateField(null=True)
    payment_terms = models.CharField(max_length=255, null=True)
    due_date = models.DateField(null=True)
    po_number = models.CharField(max_length=50, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)  # Optional field for logo
    sender = models.CharField(max_length=255, default="Sender Name")  # Default value for sender
    notes = models.TextField(null=True, blank=True, default="") # notes just added
    customer_name = models.CharField(max_length=255, default="Customer Name")  # Default value for customer_name
    # subtotal = models.DecimalField(max_digits=10, decimal_places=2) # dynamically calculated
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    shipment = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return sum(item.amount or 0 for item in self.items.all())


    @property
    def total(self):
        return (
        self.subtotal +
        (self.tax or 0) +
        (self.shipment or 0) -
        (self.discount or 0)
    )



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null=True)
    quantity = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        self.amount = (self.quantity or 0) * (self.rate or 0)
        super().save(*args, **kwargs)
