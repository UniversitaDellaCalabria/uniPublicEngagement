import math

from django.conf import settings

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 10)
    page_size_query_param = 'page_size'
    max_page_size = 250

    def get_paginated_response(self, data):
        real_page_size = int(self.request.query_params.get(
            self.page_size_query_param, 0)) or self.page_size

        return Response({
            'count': self.page.paginator.count,
            # 'next': self.url_refactor(self.get_next_link()),
            'next': self.get_next_link(),
            # 'previous': self.url_refactor(self.get_previous_link()),
            'previous': self.get_previous_link(),
            # 'page': int(self.request.query_params.get('page', 1)),
            "page_number": self.page.number,
            'per_page': real_page_size,
            'total_pages': math.ceil(self.page.paginator.count / real_page_size),
            'results': data,
        })
