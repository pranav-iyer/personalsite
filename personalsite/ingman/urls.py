from dataclasses import field
from re import L
from syslog import LOG_UUCP

from django.urls import include, path
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework import routers, serializers, viewsets

from .models import IngInstance, IngredientType

"""
Frontend use cases:
1. what's in my house right now?
2. Add items that i bought at the grocery store
3. use up items (change quantity, or set exists to false)
4. 
"""


class IngredientTypeSerializer(serializers.ModelSerializer):
    # id = serializers.HyperlinkedIdentityField(view_name="ingman:ingredienttype-detail")
    class Meta:
        model = IngredientType
        fields = ["id", "name", "category", "shelf_life"]


class IngredientTypeFilterSet(filters.FilterSet):
    # name = filters.Filter(field_name='name', lookup_expr='search')
    # name_exact = filters.Filter(field_name='name', lookup_expr='iexact')
    class Meta:
        model = IngredientType
        fields = ["name", "category"]


class IngredientTypeViewSet(viewsets.ModelViewSet):
    queryset = IngredientType.objects.all()
    serializer_class = IngredientTypeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = IngredientTypeFilterSet


class IngInstanceSerializer(serializers.ModelSerializer):
    # id = serializers.HyperlinkedIdentityField(view_name="ingman:inginstance-detail")

    class Meta:
        model = IngInstance
        fields = ["id", "ing_type", "exists", "quantity", "location", "created"]


class IngInstanceReadSerializer(IngInstanceSerializer):
    ing_type = IngredientTypeSerializer(read_only=True)


class IngInstanceViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return IngInstanceReadSerializer
        return IngInstanceSerializer

    queryset = IngInstance.objects.all()
    filter_backends = [filters.DjangoFilterBackend, rf_filters.OrderingFilter]
    filterset_fields = ["location", "exists"]
    ordering_fields = ["ing_type__category", "ing_type__name", "quantity"]
    ordering = ["ing_type__category", "ing_type__name", "quantity"]


router = routers.DefaultRouter()
router.register(r"ingredienttypes", IngredientTypeViewSet)
router.register(r"inginstances", IngInstanceViewSet, "inginstance")

app_name = "ingman"
urlpatterns = [
    path("api/", include(router.urls)),
]
