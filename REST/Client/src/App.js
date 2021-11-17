import React from 'react'

function App() {

  // var targetContainer = document.getElementById("this-div");
  // var eventSource = new EventSource("https://localhost:8001");
  // eventSource.addEventListener('greeting', function(event){
  //     var data = JSON.parse(event.data);
  //     alert(data)
  // }, false);

  // eventSource.onmessage = function (e) {
  // };

  var source = new EventSource("{{ url_for('sse.stream') }}");
  source.addEventListener('greeting', function (event) {
    var data = JSON.parse(event.data);
    alert("The server says " + data.message);
  }, false);
  source.addEventListener('error', function (event) {
    alert("Failed to connect to event stream. Is Redis running?");
  }, false);

  return <>Oi</>
}

export default App;
