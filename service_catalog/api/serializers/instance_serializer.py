from rest_framework import serializers

from profiles.api.serializers.billing_group_serializers import BillingGroupInstanceReadSerializer
from profiles.api.serializers.user_serializers import UserSerializer
from resource_tracker.api.serializers.resource_group.resource_serializers import ResourceSerializer
from service_catalog.models import Instance, InstanceState


class InstanceReadSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)
    billing_group = BillingGroupInstanceReadSerializer(read_only=True)
    spoc = UserSerializer(read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'


class RestrictedInstanceReadSerializer(InstanceReadSerializer):
    spoc = UserSerializer(read_only=True)

    class Meta:
        model = Instance
        exclude = ["spec"]


class InstanceSerializer(serializers.ModelSerializer):
    state = serializers.ChoiceField(choices=InstanceState.choices)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Instance
        fields = '__all__'
