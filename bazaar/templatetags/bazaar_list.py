from __future__ import unicode_literals

from django import template

register = template.Library()


@register.filter
def paginator_slice(page_obj, adjacent_pages=3):
    """
    Given a Page object instance return a range of page numbers to show on pagination
    controls. Adds first and last page and ellipsis for hidden pages

    For instance, when the current page is 10 on a total of 100 pages this is the result:

        [1, '...', 7, 8, 9, 10, 11, 12, 13, '...', 100]
    """

    paginator = page_obj.paginator

    # when there are less than 15 pages return the whole range
    if paginator.num_pages < 15:
        return paginator.page_range

    current_page = page_obj.number
    end_page = paginator.num_pages
    min_page = max(1, current_page - adjacent_pages)
    max_page = min(end_page + 1, current_page + adjacent_pages + 1)

    page_numbers = list(range(min_page, max_page))

    # add first page to list whether it's missing
    if min_page > 1:
        page_numbers.insert(0, 1)

        # add ellipsis for hidden pages
        if min_page > 2:
            page_numbers.insert(1, "...")

    # add last page to list whether it's missing
    if max_page < end_page + 1:
        page_numbers.append(end_page)

        # add ellipsis for hidden pages
        if max_page < end_page:
            page_numbers.insert(-1, "...")

    return page_numbers


@register.inclusion_tag("bazaar/sort_direction.html", takes_context=True)
def sort_direction(context, sort_field):
    return {
        "is_sorted": sort_field["is_current"],
        "sort_ascending": context["current_sort_direction"] != "-",
    }


@register.filter
def get_url(obj, path, endpoint='detail'):
    tokenized_paths = path.split('.')
    for path in tokenized_paths:
        if hasattr(obj, path):
            obj = getattr(obj, path)
    url_product_path = obj.__class__.objects.get_subclass(id=obj.id).__class__.__name__.lower()
    if url_product_path == 'compositeproduct':
        url_product_path = 'product'
    path = "{}-{}".format(url_product_path, endpoint)
    return path
