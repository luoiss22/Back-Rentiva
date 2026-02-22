from rest_framework import serializers
from .models import DatosFiscales


class DatosFiscalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosFiscales
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
