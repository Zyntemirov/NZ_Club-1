import django_filters
from cashbox.models import Transfer


class TransferHistoryUserFilter(django_filters.FilterSet):
    create_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Transfer
        fields = ['create_at',]