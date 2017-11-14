# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from gripcontrol import HttpStreamFormat
from django_grip import set_hold_stream, publish
import fastly
from .models import Counter

def counter(request, counter_id):
	c = get_object_or_404(Counter, name=counter_id)

	if request.method == 'OPTIONS':
		return HttpResponse()
	elif request.method == 'GET':
		return HttpResponse(str(c.value) + '\n', content_type='text/plain')
	elif request.method == 'POST':
		prev = c.incr()

		fa = fastly.API()
		fa.authenticate_by_key(settings.FASTLY_API_KEY)
		fa.purge_url(settings.FASTLY_DOMAIN, reverse('stream', args=[c.name]))

		publish(
			'counter-%s' % counter_id,
			HttpStreamFormat('event: message\ndata: %s\n\n' % str(c.value)),
			id=str(c.value),
			prev_id=str(prev))
		return HttpResponse(str(c.value) + '\n', content_type='text/plain')
	else:
		return HttpResponseNotAllowed(['OPTIONS', 'GET', 'POST'])

def stream(request, counter_id):
	c = get_object_or_404(Counter, name=counter_id)

	if request.method == 'OPTIONS':
		return HttpResponse()
	elif request.method == 'GET':
		body = ':' + (' ' * 2048) + '\n\n'
		body += 'event: message\ndata: %s\n\n' % c.value
		set_hold_stream(request, 'counter-%s' % counter_id)
		return HttpResponse(body, content_type='text/event-stream')
	else:
		return HttpResponseNotAllowed(['OPTIONS', 'GET'])
