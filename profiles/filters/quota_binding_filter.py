from profiles.models import QuotaBinding
from Squest.utils.squest_filter import SquestFilter


class QuotaBindingFilter(SquestFilter):
    class Meta:
        model = QuotaBinding
        fields = ['quota__name']
