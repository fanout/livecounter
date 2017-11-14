---
layout: page
---

The Live Counter Demo is a counter API with live updates. You can increment integers and monitor them for changes. It is being used on this page to display page hits (inspired by [rauchg's blog](https://rauchg.com/essays)):

<div id="overlay" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; z-index:999; background-color: white;"></div>
<div><span id="hits-area">Page hits: <span id="hits"></span></span></div>
<script>
  $(function() {
    var url = 'http://api.livecounter.org/counters/1/';
    var firstValue = true;
    var es = new EventSource(url);
    es.addEventListener('message', function (e) {
      $('#hits').text(e.data);
      if (firstValue) {
        firstValue = false;
        $('#overlay').hide();
        // after receiving initial value, increment counter
        $.post(url, function () {});
      } else {
        // highlight animation for updates after initial value
        $('#hits-area').effect('highlight', {}, 1000);
      }
    }, false);
  });
</script>
<p></p>

Of course, the counters provided by this API could be used for things other than page hits or display.

This project uses a high scalability architecture based on [Fanout](https://fanout.io) (for handling HTTP streaming connections) and [Fastly](https://www.fastly.com/) (for caching last values and Fanout instructions). For background, see [this article](#).

## API

Counter resources are accessible using the form:

`http://api.livecounter.org/counters/{counter-id}/`

The demo service at `api.livecounter.org` has 9 counters available (IDs 1-9). Counter ID 1 is being used to display hits to this website. You can use IDs 2-9 for playing around. For real world use, you should deploy your own server instance. The [code is here](https://github.com/fanout/livecounter).

### Listening to a counter value

To retrieve a counter's current value and listen for updates, make a `GET` request to the counter resource with the `Accept` header set to `text/event-stream`:

```http
GET /counters/2/ HTTP/1.1
Host: api.livecounter.org
Accept: text/event-stream
```

You'll receive a streaming response containing the current value:

```http
HTTP/1.1 200 OK
Transfer-Encoding: chunked
Connection: Transfer-Encoding
Content-Type: text/event-stream

event: message
data: 26
```

When the counter changes, new values will be streamed out over the existing response:

```
event: message
data: 27

event: message
data: 28
```

### Incrementing a counter

To increment a counter's value, make a `POST` request to its resource:

```http
POST /counters/2/ HTTP/1.1
Host: api.livecounter.org
Content-Length: 0
```

The updated value will be pushed to any listening connections.

## Page hits

This website implements a page hit counter like this:

```js
var url = 'http://api.livecounter.org/counters/1/';
var firstValue = true;
var es = new EventSource(url);
es.addEventListener('message', function (e) {
  $('#hits').text(e.data);
  if (firstValue) {
    firstValue = false;
    // after receiving initial value, increment counter
    $.post(url, function () {});
  } else {
    // highlight animation for updates after initial value
    $('#hits-area').effect('highlight', {}, 1000);
  }
}, false);
```
