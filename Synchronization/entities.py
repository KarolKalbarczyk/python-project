from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from __init__ import db
class SynchStatus(Enum):
    OK = 0
    Failure = 1


class SynchAction(Enum):
    Added = 0
    Deleted = 1
    ModifiedQuantity = 2
    ModifiedPrice = 3


class Synchronization(db.Model):
    __tablename__ = 'synchronizations'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    status = db.Column(db.Enum(SynchStatus))
    logs = relationship("SynchLog", back_populates = "synchronization")

    def get_number_of_modifications(self):
        uniqueCodes = set()
        for log in self.logs:
            uniqueCodes.add(log.productCode)

        return len(uniqueCodes)

    # def __repr__(self):
    # return "<Product(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


class SynchLog(db.Model):
    __tablename__ = 'synchlogs'

    id = db.Column(db.Integer, primary_key=True)
    productCode = db.Column(db.String)
    synchronizationId = db.Column(db.Integer, ForeignKey('synchronizations.id'))
    synchronization = relationship("Synchronization", back_populates = "logs")
    action = db.Column(db.Enum(SynchAction))
    original = db.Column(db.String)
    new = db.Column(db.String)

