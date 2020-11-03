import django_filters
from .models import Item, Category
from django_filters import rest_framework as filters


class ItemFilter(django_filters.FilterSet):
    

    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Decending')
    )    
    ordering = django_filters.ChoiceFilter(label='Ordering', choices=CHOICES, method='filter_by_order')
   

    class Meta:
        model = Item
        fields = {
            'title':['icontains'],
            'price': ['lt', 'gt'],
            
        }
    def filter_by_order(self,queryset,name,value):
        expression = 'pub_date' if value=='ascending' else '-pub_date'
        return queryset.order_by(expression)