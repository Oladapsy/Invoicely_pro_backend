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
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'date', 'payment_terms', 'due_date',
            'po_number', 'logo', 'sender', 'notes', 'customer_name', 'subtotal',
            'tax', 'discount', 'shipment', 'amount_paid', 'balance_due', 'items', 'status'
        )
        read_only_fields = ('user', 'subtotal')  # Prevent user and subtotal from being updated via API

        extra_kwargs = {
            'logo': {'required': False, 'allow_null': True},  # Make logo optional
        }

    def create(self, validated_data):
        """
        Handles creation of an invoice and its related line items.
        Ensures that line items are properly associated with the created invoice.
        """
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)

        # Create associated invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        # Extract the items from validated data
        items_data = validated_data.pop('items', [])

        # Update the invoice instance fields (excluding items)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save updated invoice fields

        # Handle the invoice items
        # Step 1: Find the existing invoice items
        existing_items = {item.id: item for item in instance.items.all()}

        # Step 2: Handle updating existing items or creating new ones
        incoming_item_ids = [item_data.get('id') for item_data in items_data if item_data.get('id')]

        # Process incoming items
        for item_data in items_data:
            item_id = item_data.get('id')

            if item_id:
                # Update the existing item
                item = existing_items.pop(item_id, None)
                if item:
                    item.description = item_data.get('description', item.description)
                    item.quantity = item_data.get('quantity', item.quantity)
                    item.rate = item_data.get('rate', item.rate)
                    item.amount = item_data.get('amount', item.amount)
                    item.save()
            else:
                # Create a new item
                InvoiceItem.objects.create(invoice=instance, **item_data)

        # Step 3: Remove items that are no longer part of the request
        for item in existing_items.values():
            item.delete()

        return instance
