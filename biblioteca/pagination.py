from rest_framework.pagination import LimitOffsetPagination

class LimitOffsetPaginationWithUpperBound(LimitOffsetPagination):
    # Define um limite máximo para o número de itens por página
    max_limit = 5
