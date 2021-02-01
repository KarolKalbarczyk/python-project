import datetime
import urllib.request
import os
from gettext import gettext
from __init__ import app
from flask import json
from sqlalchemy.orm import joinedload

from Synchronization.product_dto import ProductDTO
from database_definition import db
from Synchronization.entities import SynchStatus, SynchAction, Synchronization, SynchLog
from order.entities import ProductSnapshot, OrderStatus, Order, OrderHasProducts
from product.entities import Vote, ProductCategory, Product
from utils import flat_map


class SynchronizationService():

    def synchronize(self):
        warehouses = os.getenv('warehouses').split(',')
        responses = [self.__get_from_erp(warehouse) for warehouse in warehouses]
        models = self.__join_responses(responses)

        if models is None:
            db.session.add(Synchronization(date = datetime.date.today(), status = SynchStatus.Failure))
            db.session.commit()
            return

        products = { product.code : product for product in Product.query.all() }
        snapshotList = flat_map( lambda order: order.snapshots, Order.query.options(joinedload('snapshots')).filter_by(status = OrderStatus.Finalized).all())
        snapshots = { s.code: s for s in snapshotList}
        synchronization = Synchronization(date = datetime.date.today(), status = SynchStatus.OK)
        session = db.session()

        self.__modify_changed_products(models, products, snapshots, synchronization)
        self.__create_new_products(models, session, synchronization)

        session.add(synchronization)
        session.commit()

    def __modify_changed_products(self, models, products, snapshots, synchronization):
        for product in products.values():
            snapshot = snapshots.get(product.code)
            snapshotQuantity = snapshot.quantity if snapshot is not None else 0
            model = models.get(product.code)
            if model is None:
                synchronization.logs.append(SynchLog(productCode=product.code, action=SynchAction.Deleted))
                Vote.query.filter_by(productId = product.id).delete()
                OrderHasProducts.query.filter_by(productId = product.id).delete()
                db.session.commit()
                Product.query.filter_by(code = product.code).delete()
            else:
                if model.quantity != product.quantity + snapshotQuantity:
                    synchronization.logs.append(SynchLog(productCode=product.code, action=SynchAction.ModifiedQuantity, original = product.quantity, new = model.quantity))
                    product.quantity = model.quantity - snapshotQuantity

                    if product.quantity < 0:
                        app.logger.info(f"something went wrong when updating product with a code of {product.code}, there's less items in warehouse than expected")#in reality, this would occur only if something was stolen from the warehouse
                        pass

                if product.name != model.name:
                    app.logger.info(f"names of product {product.code} and its model not the same")
                    pass
                del models[product.code]

    def __create_new_products(self, models, session, synchronization):
        for model in models.values():
            product = Product(name=model.name, code=model.code, quantity=model.quantity, category = ProductCategory(model.category))
            synchronization.logs.append(SynchLog(productCode=product.code, action=SynchAction.Added))
            session.add(product)

    def get_synchronization(self, synchId):
        synchronization = Synchronization.query.options(joinedload('logs')).get(synchId)

        if synchronization is None:
            return None, None

        actions = []
        for log in synchronization.logs:
            if (log.action == SynchAction.Added):
                actions.append(gettext('product with code %s was added') % log.productCode)
            if (log.action == SynchAction.Deleted):
                actions.append(gettext('product with code %s was deleted') % log.productCode)
            if (log.action == SynchAction.ModifiedQuantity):
                actions.append(gettext('product with code %s has changed quantity from %s to %s') % (
                log.productCode, log.original, log.new))

        return synchronization, actions

    def __get_from_erp(self, warehouse):
        url = os.getenv(warehouse)
        retries = int(os.getenv('retries'))
        while retries > 0:
            try:
                resp = urllib.request.urlopen(url).read().decode()
                response = json.loads(resp)
                return { x['code']: ProductDTO(
                    name = x['name'],
                    code = ['code'],
                    quantity = int(x['quantity']),
                    category = x['category']) for x in response.values()}

            except Exception as ex:
                app.logger.info("something wen wrong when truing to connect to warehouse " + warehouse)
                retries -= 1

        return None

    def __join_responses(self, responses):
        models = {}
        codeSet = { code for response in responses for code in response}
        for code in codeSet:
            dtos = [ response.get(code) for response in responses if response.get(code)]
            totalQuantity = sum(p.quantity for p in dtos)

            if any(dto.name != dtos[0].name for dto in dtos):
                app.logger.info(f"names of product with code {code} i different warehouses are not the same")
                pass
            models[code] = ProductDTO(quantity = totalQuantity, name = dtos[0].name, code = code, category= dtos[0].category)

        return models

