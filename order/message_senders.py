from abc import ABC, abstractmethod

from Email.email_service import EmailService


class MessageSender(ABC):

    @abstractmethod
    def send_message(self, address, orderId):
        pass


class EmailSender(MessageSender):

    def send_message(self, address, orderId):
        service = EmailService()
        message = f"""
        Hello 

        Your order with an id of a {orderId} has been finalized.
        """
        service.send_email(address, message)

class PassiveSender(MessageSender):

    def send_message(self, address, orderId):
        pass


class FaxSender(MessageSender, ABC):
    def send_message(self, message):
        pass