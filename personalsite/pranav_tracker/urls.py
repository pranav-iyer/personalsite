from django.urls import include, path
from rest_framework import routers, serializers, viewsets

from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "timestamp",
            "latitude",
            "longitude",
            "position_accuracy",
            "altitude",
            "altitude_accuracy",
            "heading",
            "speed",
        ]


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


router = routers.DefaultRouter()
router.register(r"locations", LocationViewSet)

app_name = "pranav_tracker"

urlpatterns = [
    path("api/", include(router.urls)),
]
