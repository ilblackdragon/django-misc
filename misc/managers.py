from django.db import models
from django.db.models.query import QuerySet


class SoftDeleteQuerySet(QuerySet):
	"""Query set for soft delete manager."""

	def delete(self):
		return super(SoftDeleteQuerySet, self).update(alive=False)

	def hard_delete(self):
		return super(SoftDeleteQuerySet, self).delete()

	def alive(self):
		return self.filter(alive=True)

	def deleted(self):
		return self.exclude(alive=True)


class SoftDeleteManager(models.Manager):
	"""Manager provides soft deletion of records.

	Your model must have BooleanField or LiveField "alive".
	"""

	def get_query_set(self):
		return SoftDeleteQuerySet(self.model, using=self._db).alive()

	def all_with_deleted(self):
		return SoftDeleteQuerySet(self.model, using=self._db)

	def deleted(self):
		return SoftDeleteQuerySet(self.model, using=self._db).deleted()

	def hard_delete(self):
		return self.get_query_set().hard_delete()

	def get(self, *args, **kwargs):
		"""If specific record was requested, return if even if it's deleteted."""
		return self.all_with_deleted.get(*args, **kwargs)

	def filter(self, *args, **kwargs):
		"""If id or pk was specified as a kwargs, return even if it's deleteted."""
		if 'pk' in kwargs or 'id' in kwargs:
			return self.all_with_deleted().filter(*args, **kwargs)
		return self.get_query_set().filter(*args, **kwargs)
