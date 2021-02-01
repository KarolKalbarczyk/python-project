import datetime
import urllib.request
import os
from gettext import gettext
from urllib import request
from __init__ import app
from flask import json
from sqlalchemy.orm import joinedload


class OrderRequestService():

    def request_products(self, snapshots):
        warehouses = os.getenv('warehouses').split(',')
        codeToRequirement = { p.code: p.quantity for p in snapshots }
        for warehouse in warehouses:
            if len(codeToRequirement) == 0:
                return
            response = self.__send_request(warehouse, codeToRequirement)

            for code, value in response.items():
                codeToRequirement[code] -= value
                if codeToRequirement[code] == 0:
                    del codeToRequirement[code]
        if len(codeToRequirement) != 0:
            app.logger.info(f'something went wrong during request for order with product codes {"".join(map(lambda s: s.code + " ", snapshots))}')

    def __send_request(self, warehouse, requirements):
        url = os.getenv(warehouse)
        data = json.dumps({'requirements': requirements})
        body = data.encode('utf-8')
        req = request.Request(url + 'order', data=body)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        return json.loads(request.urlopen(req).read().decode())


