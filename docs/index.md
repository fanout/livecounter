---
layout: page
---

Counter:

<div id="counter"></div>
<script>
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if(xhr.readyState == 4) {
            var es = new EventSource('http://api.livecounter.org/counters/1/stream/');
            es.addEventListener('message', function (e) {
                var el = document.getElementById('counter');
                el.innerText = e.data;
            }, false);
        }
    };
    xhr.open('POST', 'http://api.livecounter.org/counters/1/');
    xhr.send();
</script>
