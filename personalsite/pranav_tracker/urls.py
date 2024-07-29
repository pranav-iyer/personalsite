from django.urls import include, path
from django_filters import rest_framework as filters
from rest_framework import routers, serializers, viewsets

from . import views
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "timestamp",
            "latitude",
            "longitude",
            "position_accuracy",
            "altitude",
            "altitude_accuracy",
            "heading",
            "speed",
        ]


class LocationFilterSet(filters.FilterSet):
    view_date = filters.Filter(field_name="timestamp", lookup_expr="date")


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().filter(position_accuracy__lte=300)
    serializer_class = LocationSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = LocationFilterSet


router = routers.DefaultRouter()
router.register(r"locations", LocationViewSet)

app_name = "pranav_tracker"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include(router.urls)),
]
