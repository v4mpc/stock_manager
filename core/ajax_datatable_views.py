from ajax_datatable.views import AjaxDatatableView
from django.contrib.auth.models import Permission
from .models import Sale


class PermissionAjaxDatatableView(AjaxDatatableView):
    model = Sale
    title = 'Sales'
    initial_order = [["id", "dsc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        # AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': True, },
        {'name': 'created_at', 'visible': True, },
        {'name': 'product_name', 'visible': True, },
        {'name': 'quantity', 'visible': True, },
        {'name': 'buy_price', 'visible': True, },
        {'name': 'sale_price', 'visible': True, },

    ]
