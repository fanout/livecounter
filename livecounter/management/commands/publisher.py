import time
import json
import threading
import traceback
import redis
import fastly
from django.conf import settings
from django.urls import reverse
from django.core.management.base import BaseCommand
from gripcontrol import HttpStreamFormat
from django_grip import publish
from livecounter.models import Counter
from livecounter.utils import sse_encode

SEND_DELAY = 1000
SEND_CHECK = 100

class Command(BaseCommand):
	help = 'Publish rate-limited live updates.'

	def _purge_and_publish(self, name, value):
		self.stdout.write('outputting: %s=%d' % (name, value))

		# purge from fastly cache
		fa = fastly.API()
		fa.authenticate_by_key(settings.FASTLY_API_KEY)
		fa.purge_url(settings.FASTLY_DOMAIN, reverse('stream', args=[name]))

		# publish through fanout
		publish('counter-%s' % name, HttpStreamFormat(sse_encode(value)))

	def _handle_redis_message(self, r, data_raw):
		try:
			data = json.loads(data_raw)
		except Exception:
			self.stderr.write('failed to parse as json: %s' % data_raw)
			return

		self.stdout.write('%s' % repr(data))

		name = data['name']
		value = data['value']

		try:
			if r.exists('counter-sent-%s' % name):
				r.sadd('counter-need-send', name)
			else:
				r.psetex('counter-sent-%s' % name, SEND_DELAY, 1)
				self._purge_and_publish(name, value)
		except Exception:
			self.stderr.write(
				'error handling message: %s' % traceback.format_exc())

	def _handle_need_send(self, r):
		while True:
			try:
				for name in r.smembers('counter-need-send'):
					c = Counter.objects.get(name=name)
					value = c.value
					if not r.exists('counter-sent-%s' % name):
						r.psetex('counter-sent-%s' % name, SEND_DELAY, 1)
						r.srem('counter-need-send', name)
						self._purge_and_publish(name, value)
				time.sleep(SEND_CHECK * 0.001)
			except Exception:
				self.stderr.write(
					'error handling need send: %s' % traceback.format_exc())
				time.sleep(2)

	def handle(self, *args, **options):
		r = redis.Redis()

		need_send_thread = threading.Thread(target=self._handle_need_send, args=(r,))
		need_send_thread.daemon = True
		need_send_thread.start()

		# run in loop to reconnect if disconnected
		while True:
			try:
				p = r.pubsub()
				p.subscribe('updates')

				for m in p.listen():
					mtype = m['type']
					if mtype == 'subscribe':
						self.stdout.write(
							'subscribed to redis channel: %s' % m['channel'])
					elif mtype == 'message':
						self._handle_redis_message(r, m['data'])

			except Exception:
				self.stderr.write('failed to read message')
				time.sleep(2)
