# Generated by Django 5.1.4 on 2025-01-08 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0009_alter_invoice_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='balance_due',
        ),
    ]
