from enum import Enum

def get_enum_list(enum):
    return list(map(lambda x: x.value, enum))

class InvoiceOptions(Enum):
    Normal = 'normal'
    Proforma = 'proforma'

class MessageOptions(Enum):
    Email = 'email'
    Fax = 'fax'
