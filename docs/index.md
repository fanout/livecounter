---
layout: page
---

Counter:

<div id="counter"></div>
<script>
    var es = new EventSource('http://api.livecounter.org/counters/1/stream/');
    es.addEventListener('message', function (e) {
        var el = document.getElementById('counter');
        el.innerText = e.data;
    }, false);
</script>
