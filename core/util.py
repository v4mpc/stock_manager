import csv
import os
import re
import uuid
from abc import ABC, abstractmethod
from datetime import date

import arrow
from core.models import (

    Product, StockOnHand

)
from django.conf import settings


class UpdateStockOnInactiveProductException(Exception):
    pass


def update_stock_on_hand(product: Product, stock_date: date, quantity: float, transaction_type: str):
    if not product.active:
        raise UpdateStockOnInactiveProductException
    try:
        obj = StockOnHand.objects.get(product=product,
                                      created_at=stock_date)
        if transaction_type == 'DR':
            obj.quantity += quantity
        else:
            obj.quantity -= quantity
        obj.save()
    except StockOnHand.DoesNotExist:
        new_values = {"product": product, "created_at": stock_date, "quantity": quantity}
        obj = StockOnHand(**new_values)
        obj.save()


def extract_quantity(queryset):
    return queryset.values().get()['quantity']


def get_stock_on_hand(product: Product, stock_date: date):
    result = StockOnHand.objects.filter(product=product)
    if result.count() == 1:
        return extract_quantity(result)
    elif result.count() == 0:
        return 0.0
    else:
        result = result.filter(created_at__lte=stock_date)
        if result.count() == 1:
            return extract_quantity(result)
        elif result.count() > 1:
            return result.latest('created_at').quantity
        else:
            return 0.0
