from django.db.models import QuerySet, Manager, Q
from django.utils import timezone
from django.contrib.auth.models import UserManager


class SoftQuerySet(QuerySet):
    def delete(self):
        super().update(is_deleted=True, deleted_at=timezone.now())


class SoftManager(Manager):
    def get_queryset(self):
        return SoftQuerySet(self.model, using=self._db).filter(Q(is_deleted=False) | Q(is_deleted=None))
