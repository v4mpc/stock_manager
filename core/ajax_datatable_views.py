from ajax_datatable.views import AjaxDatatableView
from django.contrib.auth.models import Permission
from django.db.models import F, Sum

from .models import Sale, Expense


class ProductSaleAjaxDatatableView(AjaxDatatableView):
    model = Sale
    title = 'Sales'
    initial_order = [["created_at", "dsc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        # AjaxDatatableView.render_row_tools_column_def(),
        # {'name': 'id', 'visible': True, },
        {'name': 'created_at', 'visible': True, 'title': 'Date'},
        {'name': 'product_name', 'visible': True, },
        {'name': 'quantity', 'visible': True, 'title': 'Sold QTY'},
        {'name': 'buy_price', 'visible': True, },
        {'name': 'sale_price', 'visible': True, },
        {'name': 'profit', 'visible': True, 'title': 'Profit'},
        {'name': 'total_profit', 'visible': True, 'title': 'Total Profit'},

    ]

    # def footer_message(self, qs, params):
    #     print(params)
    #     return 'Selected rows: %d' % qs.aggregate(grand_total=Sum('total_profit'))['grand_total']

    def get_initial_queryset(self, request=None):
        return Sale.objects.annotate(profit=F("sale_price") - F("buy_price"), total_profit=F('profit') * F('quantity'))


class ExpenseAjaxDatatableView(AjaxDatatableView):
    model = Expense
    title = 'Expense'
    initial_order = [["created_at", "dsc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        {'name': 'created_at', 'visible': True, 'title': 'Date'},
        {'name': 'name', 'visible': True, },
        {'name': 'amount', 'visible': True},

    ]

    # def footer_message(self, qs, params):
    #     print(params)
    #     return 'Selected rows: %d' % qs.aggregate(grand_total=Sum('total_profit'))['grand_total']
    #
    # def get_initial_queryset(self, request=None):
    #     return Sale.objects.annotate(profit=F("sale_price") - F("buy_price"), total_profit=F('profit') * F('quantity'))
