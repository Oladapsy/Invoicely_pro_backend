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
from os.path import join, exists
from django.conf import settings




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
        # print('i am being called')
        serializer.save(user=self.request.user)
        


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# newest pdf generator

# def generate_pdf_content(invoice):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)

#     # Page dimensions
#     width, height = letter
#     margin = 50

#     # Header Section - Add Logo if it exists
#     if invoice.logo and invoice.logo.name:
#         # Construct the logo path
#         logo_path = f"{settings.MEDIA_ROOT}/{invoice.logo.name}"
#         print(f"Logo path: {logo_path}")  # Debug statement

#         try:
#             # Attempt to draw the logo
#             p.drawImage(logo_path, margin, height - 100, width=100, height=50, preserveAspectRatio=True, anchor='c')
#         except Exception as e:
#             # Log any error that occurs while drawing the logo
#             print(f"Error rendering logo: {e}")
#     else:
#         print("Invoice has no logo or logo name is invalid.")  # Debug statement for missing or invalid logo

#     # Title Section
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
#     p.drawString(margin + 200, height - 160, f"{invoice.customer_name}")

#     # Payment Terms and PO Number
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(margin, height - 200, "Payment Terms")
#     p.drawString(margin + 200, height - 200, "PO Number")

#     p.setFont("Helvetica", 10)
#     p.drawString(margin, height - 220, f"{invoice.payment_terms}")
#     p.drawString(margin + 200, height - 220, f"{invoice.po_number}")

#     # Table Headers
#     table_data = [["ITEM", "QUANTITY", "RATE", "AMOUNT"]]
#     for item in invoice.items.all():
#         table_data.append([item.description, str(item.quantity), f"US${item.rate:.2f}", f"US${item.amount:.2f}"])

#     # Add Subtotal, Tax, Discount, Shipment, and Total
#     table_data.append(["", "", "Subtotal", f"US${invoice.subtotal:.2f}"])
#     table_data.append(["", "", "Tax", f"US${invoice.tax or 0.0:.2f}"])
#     table_data.append(["", "", "Discount", f"-US${invoice.discount or 0.0:.2f}"])
#     table_data.append(["", "", "Shipment", f"US${invoice.shipment or 0.0:.2f}"])
#     table_data.append(["", "", "Total", f"US${invoice.total:.2f}"])

#     # Create the table
#     table = Table(table_data, colWidths=[250, 75, 75, 75])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
#         ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center-align quantity, rate, and amount
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Inner grid lines
#         ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Border around table
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font bold
#         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Body font normal
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),  # Alternate row background
#     ]))

#     # Draw the table
#     table.wrapOn(p, margin, height - 500)
#     table.drawOn(p, margin, height - 500 - len(table_data) * 20)

#     # Notes Section
#     notes_y = height - 500 - len(table_data) * 20 - 40
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(margin, notes_y, "Notes:")
#     p.setFont("Helvetica", 10)
#     p.drawString(margin, notes_y - 20, invoice.notes or "No additional notes.")

#     # Footer
#     footer_y = notes_y - 60
#     p.setFont("Helvetica-Bold", 10)
#     p.drawString(margin, footer_y, "Terms and Conditions:")
#     p.setFont("Helvetica", 10)
#     p.drawString(margin, footer_y - 20, "All sales are final. Payment must be made within the specified terms.")

#     # Finish PDF
#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer.getvalue()


def generate_pdf_content(invoice):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Page dimensions
    width, height = letter
    margin = 50

    # Header Section - Add Logo if it exists
    if invoice.logo and invoice.logo.name:
        # Construct the logo path
        logo_path = f"{settings.MEDIA_ROOT}/{invoice.logo.name}"
        print(f"Logo path: {logo_path}")  # Debug statement

        try:
            # Attempt to draw the logo
            p.drawImage(logo_path, margin, height - 100, width=100, height=50, preserveAspectRatio=True, anchor='c')
        except Exception as e:
            # Log any error that occurs while drawing the logo
            print(f"Error rendering logo: {e}")
    else:
        print("Invoice has no logo or logo name is invalid.")  # Debug statement for missing or invalid logo

    # Title Section
    p.setFont("Helvetica-Bold", 16)
    p.drawString(width - 200, height - 50, "INVOICE")
    p.setFont("Helvetica", 10)
    p.drawString(width - 200, height - 65, f"#{invoice.invoice_number}")
    p.drawString(width - 200, height - 80, f"Date: {invoice.date}")
    p.drawString(width - 200, height - 95, f"Due Date: {invoice.due_date}")

    # Sender and Customer Information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, height - 140, f"Bill To")
    p.drawString(margin + 200, height - 140, f"Ship To")

    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 160, f"{invoice.customer_name}")
    p.drawString(margin + 200, height - 160, f"{invoice.customer_name}")

    # Payment Terms and PO Number
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, height - 200, "Payment Terms")
    p.drawString(margin + 200, height - 200, "PO Number")

    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 220, f"{invoice.payment_terms}")
    p.drawString(margin + 200, height - 220, f"{invoice.po_number}")

    # Table Headers
    table_data = [["ITEM", "DESCRIPTION", "QUANTITY", "RATE", "AMOUNT"]]
    for item in invoice.items.all():
        table_data.append([
            'Item',  # Placeholder for static "Item" column
            item.description,  # Use 'description' field from InvoiceItem model
            str(item.quantity),
            f"US${item.rate:.2f}",
            f"US${item.amount:.2f}"
        ])

    # Add Subtotal, Tax, Discount, Shipment, Total, and Balance Due
    table_data.append(["", "", "Subtotal", f"US${invoice.subtotal:.2f}"])
    table_data.append(["", "", "Tax", f"{invoice.tax or 0.0:.2f}%"])
    table_data.append(["", "", "Discount", f"-US${invoice.discount or 0.0:.2f}"])
    table_data.append(["", "", "Shipment", f"US${invoice.shipment or 0.0:.2f}"])
    table_data.append(["", "", "Total", f"US${invoice.total:.2f}"])
    table_data.append(["", "", "Balance Due", f"US${invoice.balance_due:.2f}"])

    # Create the table
    table = Table(table_data, colWidths=[200, 150, 75, 75, 75])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Center-align quantity, rate, and amount
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Inner grid lines
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Border around table
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font bold
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Body font normal
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),  # Alternate row background
    ]))

    # Draw the table
    table.wrapOn(p, margin, height - 500)
    table.drawOn(p, margin, height - 500 - len(table_data) * 20)

    # Notes Section
    notes_y = height - 500 - len(table_data) * 20 - 40
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, notes_y, "Notes:")
    p.setFont("Helvetica", 10)
    p.drawString(margin, notes_y - 20, invoice.notes or "No additional notes.")

    # Footer
    footer_y = notes_y - 60
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, footer_y, "Terms and Conditions:")
    p.setFont("Helvetica", 10)
    p.drawString(margin, footer_y - 20, "All sales are final. Payment must be made within the specified terms.")

    # Finish PDF
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

