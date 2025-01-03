# invoices/serializers.py
# make the invoice model callable over api
from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ('id', 'description', 'quantity', 'rate', 'amount')

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = ('id', 'invoice_number', 'date', 'payment_terms', 'due_date', 'po_number', 'subtotal', 'tax', 'discount', 'shipment', 'amount_paid', 'balance_due', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        
        # Update the invoice instance
        instance.invoice_number = validated_data.get('invoice_number', instance.invoice_number)
        instance.date = validated_data.get('date', instance.date)
        instance.payment_terms = validated_data.get('payment_terms', instance.payment_terms)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.po_number = validated_data.get('po_number', instance.po_number)
        instance.subtotal = validated_data.get('subtotal', instance.subtotal)
        instance.tax = validated_data.get('tax', instance.tax)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.shipment = validated_data.get('shipment', instance.shipment)
        instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)
        instance.balance_due = validated_data.get('balance_due', instance.balance_due)
        instance.save()

        # Update the invoice items
        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id:
                item = InvoiceItem.objects.get(id=item_id, invoice=instance)
                item.description = item_data.get('description', item.description)
                item.quantity = item_data.get('quantity', item.quantity)
                item.rate = item_data.get('rate', item.rate)
                item.amount = item_data.get('amount', item.amount)
                item.save()
            else:
                InvoiceItem.objects.create(invoice=instance, **item_data)

        return instance
