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

def generate_pdf_content(invoice):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    if invoice.logo:
        p.drawImage(f"{settings.MEDIA_ROOT}/{invoice.logo}", 50, 750, width=100, height=100)

    p.drawString(100, 730, f"Sender: {invoice.sender}")
    p.drawString(100, 710, f"Customer Name: {invoice.customer_name}")
    p.drawString(100, 690, f"Invoice Number: {invoice.invoice_number}")
    p.drawString(100, 670, f"Date: {invoice.date}")
    p.drawString(100, 650, f"Payment Terms: {invoice.payment_terms}")
    p.drawString(100, 630, f"Due Date: {invoice.due_date}")
    p.drawString(100, 610, f"PO Number: {invoice.po_number}")
    p.drawString(100, 590, f"Subtotal: {invoice.subtotal}")
    p.drawString(100, 570, f"Tax: {invoice.tax}")
    p.drawString(100, 550, f"Discount: {invoice.discount}")
    p.drawString(100, 530, f"Shipment: {invoice.shipment}")
    p.drawString(100, 510, f"Amount Paid: {invoice.amount_paid}")
    p.drawString(100, 490, f"Balance Due: {invoice.balance_due}")

    p.drawString(100, 470, "Invoice Items:")
    y = 450
    for item in invoice.items.all():
        p.drawString(120, y, f"- {item.description}: {item.quantity} x {item.rate} = {item.amount}")
        y -= 20

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