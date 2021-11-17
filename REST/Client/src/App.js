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

  var source = new EventSource("http://127.0.0.1:8000/");




  return <>Oi</>
}

export default App;
