from ajax_datatable.views import AjaxDatatableView
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from dataclasses import dataclass
from .models import Sale, Expense
from django.db import models


class ProductSaleAjaxDatatableView(AjaxDatatableView):
    model = Sale
    title = 'Sales'
    # initial_order = [["created_at", "asc"], ]
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


class ProductSaleAggregateAjaxDatatableView(AjaxDatatableView):
    model = Sale
    title = 'Sales'
    initial_order = [["product_name", "asc"], ]
    show_date_filters = True
    show_column_filters = False
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'
    disable_queryset_optimization_only = True

    column_defs = [
        # AjaxDatatableView.render_row_tools_column_def(),
        # {'name': 'id', 'visible': True, },

        {'name': 'product_name', 'visible': True, },
        {'name': 'quantity', 'visible': True, 'title': 'Sold QTY'},
        {'name': 'sale_price', 'visible': True, 'title': 'Total Profit'},

    ]

    def get_initial_queryset(self, request=None):
        if not request.user.is_authenticated:
            raise PermissionDenied
        queryset = Sale.objects.annotate(profit=F("sale_price") - F("buy_price"),
                                         total_profit=F('profit') * F('quantity'))
        # print(queryset)
        if 'date_from' in request.REQUEST:
            date_from = request.REQUEST.get('date_from')
            queryset = queryset.filter(created_at__gte=date_from)
        if 'date_to' in request.REQUEST:
            date_to = request.REQUEST.get('date_to')
            queryset = queryset.filter(created_at__lte=date_to)
        aggregated_total = queryset.values("product_name").annotate(total_profit=Sum('total_profit'),
                                                                    total_quantity=Sum('quantity'))
        all_products = [x['product_name'] for x in aggregated_total]
        new_query_set = Sale.objects.order_by('product_name').filter(product_name__in=all_products)[
                        :len(all_products)]

        for nq in new_query_set:
            print(nq.product_name)
        for ag in aggregated_total:
            for nq in new_query_set:
                if nq.product_name == ag['product_name']:
                    nq.quantity = ag['total_quantity']
                    nq.sale_price = ag['total_profit']
        query_set_list = []

        # c_queryset = {str(x["product_name"]): x for x in aggregated_total}
        # print(c_queryset)

        # for x in aggregated_total:
        #     query_set_list.append(
        #         Sale(product_name=x["product_name"], quantity=x["total_quantity"], sale_price=x["total_profit"]))
        #     # query_set_list.append(Sale.objects.order_by('product_name').distinct('product_name').annotate(
        #     total_profit=x['total_profit'],
        #     total_quantity=x['total_quantity']))
        # print(aggregated_total)
        # new_queryset = aggregated_total.union(queryset)
        # print(queryse
        # for ag in aggregated_total:
        #     new_queryset=Sale.objects.filter(pro)
        # print(query_set_list)
        return new_query_set
