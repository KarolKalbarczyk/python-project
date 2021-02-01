import os
from abc import ABC, abstractmethod
from InvoiceGenerator.api import Client, Provider, Creator, Item, Invoice
from InvoiceGenerator.pdf import SimpleInvoice, ProformaInvoice


class InvoiceGenerator(ABC):

    @abstractmethod
    def generate(self, order, clientName):
        pass


    def _get_invoice(self, order, clientName):
        client = Client(clientName)
        provider = Provider(os.getenv("company"), bank_account=os.getenv("bank_account"),
                            bank_code=os.getenv("bank_code"))
        creator = Creator(os.getenv("creator"))

        invoice = Invoice(client, provider, creator)
        for snapshot in order.snapshots:
            invoice.add_item(Item(count=snapshot.quantity, price=snapshot.price, description=snapshot.name,
                                  tax=int(os.getenv("Vat")), unit='$'))
        invoice.currency = '$'
        return invoice


class SimpleInvoiceGenerator(InvoiceGenerator):

    def generate(self, order, clientName):
        invoice = self._get_invoice(order, clientName)
        pdf = SimpleInvoice(invoice)
        name = f"{order.id}invoice.pdf"
        pdf.gen(f"{os.getenv('invoices')}{name}", generate_qr_code=True)

        return name

class ProformaInvoiceGenerator(InvoiceGenerator):

    def generate(self, order, clientName):
        invoice = self._get_invoice(order, clientName)
        pdf = ProformaInvoice(invoice)
        name = f"{order.id}invoice.pdf"
        pdf.gen(f"{os.getenv('invoices')}{name}", generate_qr_code=True)
        return name

class PassiveInvoiceGenerator(InvoiceGenerator):
    def generate(self, order, clientName):
        pass