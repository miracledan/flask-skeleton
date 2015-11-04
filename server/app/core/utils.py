# -*- coding: utf-8 -*-

def create_query_sort_condition(default_sort, sort_valid_field, sort_arg):
    orders = []
    for key in sort_arg:
        if (key in sort_valid_field):
            order = sort_arg[key] == 'asc' and sort_valid_field[key] or -sort_valid_field[key]
            orders.append(order)
    return len(orders) > 0 and orders or default_sort