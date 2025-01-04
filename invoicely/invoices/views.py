# from django.shortcuts import render
# invoices/views.py
from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# for pdf views or generator!!!
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from django.conf import settings

# the new pdf generator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime



# handle the messaging app
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework.response import Response



class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Overrides the default method to filter
        # invoices based on the authenticated user.
        # This ensures that each user can only see their own invoices.
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Overrides the default method to automatically
        # set the user field of the new invoice to the 
        # authenticated user. This associates the newly 
        # created invoice with the user who made the request.
        serializer.save(user=self.request.user)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# The pdf generator view

# def generate_pdf_content(invoice):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)

#     if invoice.logo:
#         p.drawImage(f"{settings.MEDIA_ROOT}/{invoice.logo}", 50, 750, width=100, height=100)

#     p.drawString(100, 730, f"Sender: {invoice.sender}")
#     p.drawString(100, 710, f"Customer Name: {invoice.customer_name}")
#     p.drawString(100, 690, f"Invoice Number: {invoice.invoice_number}")
#     p.drawString(100, 670, f"Date: {invoice.date}")
#     p.drawString(100, 650, f"Payment Terms: {invoice.payment_terms}")
#     p.drawString(100, 630, f"Due Date: {invoice.due_date}")
#     p.drawString(100, 610, f"PO Number: {invoice.po_number}")
#     p.drawString(100, 590, f"Subtotal: {invoice.subtotal}")
#     p.drawString(100, 570, f"Tax: {invoice.tax}")
#     p.drawString(100, 550, f"Discount: {invoice.discount}")
#     p.drawString(100, 530, f"Shipment: {invoice.shipment}")
#     p.drawString(100, 510, f"Amount Paid: {invoice.amount_paid}")
#     p.drawString(100, 490, f"Balance Due: {invoice.balance_due}")

#     p.drawString(100, 470, "Invoice Items:")
#     y = 450
#     for item in invoice.items.all():
#         p.drawString(120, y, f"- {item.description}: {item.quantity} x {item.rate} = {item.amount}")
#         y -= 20

#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer.getvalue()

# new generator design
# def generate_pdf_content(invoice):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)

#     # Page dimensions
#     width, height = letter
#     margin = 50

#     # Header Section
#     if invoice.logo:
#         p.drawImage(f"{settings.MEDIA_ROOT}/{invoice.logo}", margin, height - 100, width=50, height=50)

#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(width - 200, height - 50, "INVOICE")
#     p.setFont("Helvetica", 10)
#     p.drawString(width - 200, height - 65, f"#{invoice.invoice_number}")
#     p.drawString(width - 200, height - 80, f"Date: {invoice.date}")
#     p.drawString(width - 200, height - 95, f"Due Date: {invoice.due_date}")

#     # Sender and Customer Information
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(margin, height - 140, f"Bill To")
#     p.drawString(margin + 200, height - 140, f"Ship To")

#     p.setFont("Helvetica", 10)
#     p.drawString(margin, height - 160, f"{invoice.customer_name}")
#     # Assuming "Ship To" details are the same as the customer name; modify as needed.
#     p.drawString(margin + 200, height - 160, f"{invoice.customer_name}")

#     # Payment Terms and PO Number
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(margin, height - 200, "Payment Terms")
#     p.drawString(margin + 200, height - 200, "PO Number")

#     p.setFont("Helvetica", 10)
#     p.drawString(margin, height - 220, f"{invoice.payment_terms}")
#     p.drawString(margin + 200, height - 220, f"{invoice.po_number}")

#     # Table Header
#     p.setFont("Helvetica-Bold", 10)
#     table_start_y = height - 280
#     p.drawString(margin, table_start_y, "ITEM")
#     p.drawString(margin + 300, table_start_y, "QUANTITY")
#     p.drawString(margin + 400, table_start_y, "RATE")
#     p.drawString(margin + 500, table_start_y, "AMOUNT")

#     # Table Data
#     p.setFont("Helvetica", 10)
#     y = table_start_y - 20
#     for item in invoice.items.all():
#         p.drawString(margin, y, f"{item.description}")
#         p.drawString(margin + 300, y, f"{item.quantity}")
#         p.drawString(margin + 400, y, f"US${item.rate:.2f}")
#         p.drawString(margin + 500, y, f"US${item.amount:.2f}")
#         y -= 20


#     # Subtotal, Tax, Discount, Shipment, Total
#     p.setFont("Helvetica-Bold", 10)
#     y -= 20
#     p.drawString(margin + 400, y, "Subtotal:")
#     p.drawString(margin + 500, y, f"US${invoice.subtotal:.2f}")

#     y -= 20
#     p.drawString(margin + 400, y, "Tax (10%):")
#     p.drawString(margin + 500, y, f"US${invoice.tax:.2f}")

#     y -= 20
#     p.drawString(margin + 400, y, "Discount:")
#     p.drawString(margin + 500, y, f"-US${invoice.discount:.2f}")

#     y -= 20
#     p.drawString(margin + 400, y, "Shipment:")
#     p.drawString(margin + 500, y, f"US${invoice.shipment:.2f}")

#     y -= 20
#     p.drawString(margin + 400, y, "Total:")
#     p.drawString(margin + 500, y, f"US${invoice.total:.2f}")

#     # Notes Section
#     y -= 40
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(margin, y, "Notes:")
#     p.setFont("Helvetica", 10)
#     p.drawString(margin, y - 20, invoice.notes or "No additional notes.")

#     # Footer (Terms and Conditions)
#     y -= 60
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(margin, y, "Terms and Conditions:")
#     p.setFont("Helvetica", 10)
#     p.drawString(margin, y - 20, "All sales are final. Payment must be made within the specified terms.")

#     # Finish PDF
#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer.getvalue()


# new pdf generator copilot


def generate_pdf_content(invoice):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Page settings
    width, height = letter
    margin = 50

    # Draw Logo
    if invoice.logo:
        p.drawImage(f"{settings.MEDIA_ROOT}/{invoice.logo}", margin, height - 120, width=60, height=60)

    # Header section
    p.setFont("Helvetica-Bold", 20)
    p.drawString(width - 200, height - 70, "INVOICE")

    # Invoice details
    p.setFont("Helvetica", 10)
    p.drawString(width - 200, height - 90, f"Date: {datetime.strftime(invoice.date, '%b %d, %Y')}")
    p.drawString(width - 200, height - 110, f"Due Date: {datetime.strftime(invoice.due_date, '%b %d, %Y')}")
    p.drawString(width - 200, height - 130, f"PO Number: {invoice.po_number}")
    p.drawString(width - 200, height - 150, f"Balance Due: US${invoice.balance_due:.2f}")

    # Billing and shipping info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, height - 140, f"Bill To")
    p.drawString(margin + 200, height - 140, f"Ship To")
    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 160, f"{invoice.customer_name}")
    p.drawString(margin + 200, height - 160, f"{invoice.customer_name}")

    # Table for items
    table_data = [["ITEM", "QUANTITY", "RATE", "AMOUNT"]]
    for item in invoice.items.all():
        table_data.append([item.description, item.quantity, f"US${item.rate:.2f}", f"US${item.amount:.2f}"])

    table_data.append(["", "", "Subtotal", f"US${invoice.subtotal:.2f}"])
    table_data.append(["", "", "Tax", f"US${invoice.tax:.2f}"])
    table_data.append(["", "", "Discount", f"-US${invoice.discount:.2f}"])
    table_data.append(["", "", "Shipment", f"US${invoice.shipment:.2f}"])
    table_data.append(["", "", "Total", f"US${invoice.total:.2f}"])

    table = Table(table_data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.orange),
        ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
        ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
        ('ALIGN', (0, 0), (0, -1), "LEFT"),
    ]))

    table.wrapOn(p, margin, height - 400)
    table.drawOn(p, margin, height - 500)

    # Notes and Terms section
    y_position = 100  # Adjust the y_position based on content length
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, y_position, "Notes:")
    p.setFont("Helvetica", 10)
    p.drawString(margin + 50, y_position, invoice.notes or "No additional notes.")

    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, y_position - 20, "Terms:")
    p.setFont("Helvetica", 10)
    p.drawString(margin + 50, y_position - 20, "All sales are final. Payment must be made within the specified terms.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


class InvoicePDFView(APIView):
    def get(self, request, pk, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        
        pdf_content = generate_pdf_content(invoice)
        response.write(pdf_content)
        return response


# handle the messaging service (app)

class EmailInvoiceView(APIView):
    def post(self, request, pk, *args, **kwargs):
        recipient_email = request.data.get('recipient_email')
        if not recipient_email:
            return Response({"error": "Recipient email is required"}, status=status.HTTP_400_BAD_REQUEST)

        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        email = EmailMessage(
            subject=f'Invoice {invoice.invoice_number}',
            body='Please find the attached invoice.',
            from_email='dapoodedeyi03@gmail.com',
            to=[recipient_email]  # Use recipient email from request data
        )
        pdf_content = generate_pdf_content(invoice)
        email.attach('invoice.pdf', pdf_content, 'application/pdf')
        email.send()
        return Response({"message": "Invoice sent successfully"})