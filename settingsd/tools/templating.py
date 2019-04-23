from jinja2.defaults import DEFAULT_FILTERS


def quote_list(input_list):
            return ['"' + item + '"' for item in input_list]


DEFAULT_FILTERS['quote_list'] = quote_list
