from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):

    # Number of products returned per page by default
    page_size = 10

    # Allow clients to change the page size
    page_size_query_param = 'page_size'

    # Maximum number of products per page
    max_page_size = 50