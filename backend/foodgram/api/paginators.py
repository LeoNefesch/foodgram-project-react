from rest_framework.pagination import PageNumberPagination


class NumberPerPagePagination(PageNumberPagination):
    page_size = 6
