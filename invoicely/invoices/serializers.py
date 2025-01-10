# from rest_framework import serializers
# from .models import Invoice, InvoiceItem

# from rest_framework import serializers

# class InvoiceItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InvoiceItem
#         fields = ['description', 'quantity', 'rate', 'amount']

#     def validate(self, data):
#         data['quantity'] = data.get('quantity', 0)
#         data['rate'] = data.get('rate', 0.0)
#         data['amount'] = data['quantity'] * data['rate']
#         return data

# class InvoiceSerializer(serializers.ModelSerializer):
#     items = InvoiceItemSerializer(many=True, required=False)

#     class Meta:
#         model = Invoice
#         fields = (
#             'id', 'invoice_number', 'date', 'payment_terms', 'due_date',
#             'po_number', 'logo', 'sender', 'notes', 'customer_name', 'subtotal',
#             'tax', 'discount', 'shipment', 'amount_paid', 'balance_due', 'items', 'status'
#         )
#         read_only_fields = ('user', 'subtotal')

#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         invoice = Invoice.objects.create(**validated_data)
#         for item_data in items_data:
#             InvoiceItem.objects.create(invoice=invoice, **item_data)
#         return invoice

#     def update(self, instance, validated_data):
#         items_data = validated_data.pop('items', [])
        
#         # Update the invoice instance
#         instance.invoice_number = validated_data.get('invoice_number', instance.invoice_number)
#         instance.date = validated_data.get('date', instance.date)
#         instance.payment_terms = validated_data.get('payment_terms', instance.payment_terms)
#         instance.due_date = validated_data.get('due_date', instance.due_date)
#         instance.po_number = validated_data.get('po_number', instance.po_number)
#         instance.logo = validated_data.get('logo', instance.logo)
#         instance.sender = validated_data.get('sender', instance.sender)
#         instance.notes = validated_data.get('notes', instance.notes)
#         instance.customer_name = validated_data.get('customer_name', instance.customer_name)
#         instance.tax = validated_data.get('tax', instance.tax)
#         instance.discount = validated_data.get('discount', instance.discount)
#         instance.shipment = validated_data.get('shipment', instance.shipment)
#         instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)
#         instance.balance_due = validated_data.get('balance_due', instance.balance_due)
#         instance.status = validated_data.get('status', instance.status) 
#         instance.save()

#         # Update the invoice items
#         for item_data in items_data:
#             item_id = item_data.get('id')
#             if item_id:
#                 item = InvoiceItem.objects.get(id=item_id, invoice=instance)
#                 item.description = item_data.get('description', item.description)
#                 item.quantity = item_data.get('quantity', item.quantity)
#                 item.rate = item_data.get('rate', item.rate)
#                 item.amount = item_data.get('amount', item.amount)
#                 item.save()
#             else:
#                 InvoiceItem.objects.create(invoice=instance, **item_data)

#         return instance

from rest_framework import serializers
from .models import Invoice, InvoiceItem



class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for InvoiceItem model, handles individual line items in an invoice.
    """
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'rate', 'amount']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False}  # Allow updating existing items by ID
        }

    def validate(self, data):
        """
        Ensure amount is dynamically calculated based on quantity and rate.
        This avoids manual errors in input.
        """
        data['quantity'] = data.get('quantity', 0)
        data['rate'] = data.get('rate', 0.0)
        data['amount'] = data['quantity'] * data['rate']
        return data


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model, includes nested handling of InvoiceItemSerializer.
    """
    items = InvoiceItemSerializer(many=True, required=False)  # Nested serializer for related items

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'date', 'payment_terms', 'due_date',
            'po_number', 'logo', 'sender', 'notes', 'customer_name', 'subtotal',
            'tax', 'discount', 'shipment', 'amount_paid', 'balance_due', 'items', 'status'
        )
        read_only_fields = ('user', 'subtotal')  # Prevent user and subtotal from being updated via API

    def create(self, validated_data):
        """
        Handles creation of an invoice and its related line items.
        Ensures that line items are properly associated with the created invoice.
        """
        # Extract items data from the validated input
        items_data = validated_data.pop('items', [])

        # Create the invoice instance
        invoice = Invoice.objects.create(**validated_data)

        # Create associated invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        """
        Handles updates to an existing invoice and its associated line items.
        Supports partial updates to either the invoice or the items.
        """
        # Extract items data from the validated input
        items_data = validated_data.pop('items', [])

        # Update invoice fields dynamically based on provided validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save updated invoice fields

        # Process updates or additions for related invoice items
        for item_data in items_data:
            item_id = item_data.get('id')  # Look for the item's ID to determine if it exists

            if item_id:
                # Update existing item if ID is provided
                item = InvoiceItem.objects.get(id=item_id, invoice=instance)
                for attr, value in item_data.items():
                    setattr(item, attr, value)
                item.save()
            else:
                # Create new item if ID is not provided
                InvoiceItem.objects.create(invoice=instance, **item_data)

        return instance


