# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, transaction

class Counter(models.Model):
	name = models.CharField(max_length=64, unique=True)
	value = models.IntegerField(default=0)

	def incr(self):
		with transaction.atomic():
			prev = self.value
			self.value += 1
			self.save()
		return prev
