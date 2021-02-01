from abc import ABC, abstractmethod

from order.invoice_generator import SimpleInvoiceGenerator, ProformaInvoiceGenerator, PassiveInvoiceGenerator
from order.message_senders import EmailSender, PassiveSender
from order.order_enums import MessageOptions, InvoiceOptions


class OptionsFabric(ABC):

    @abstractmethod
    def get_message_service(self, paymentOption: MessageOptions):
        pass

    @abstractmethod
    def get_invoice_service(self, invoiceOption: InvoiceOptions):
        pass



class OptionsFabricImpl(OptionsFabric):

    def get_invoice_service(self, invoiceOption: InvoiceOptions):
        if invoiceOption == InvoiceOptions.Normal.value:
            return SimpleInvoiceGenerator()
        elif invoiceOption == InvoiceOptions.Proforma.value:
            return ProformaInvoiceGenerator()
        else:
            return PassiveInvoiceGenerator()

    def get_message_service(self, paymentOption: MessageOptions):
        if paymentOption == MessageOptions.Email.value:
            return EmailSender()
        elif paymentOption == MessageOptions.Fax.value:
            return None
        else:
            return PassiveSender()