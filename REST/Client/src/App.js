import React from 'react'

function App() {

  var source = new EventSource("http://127.0.0.1:8000/");

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", 'http://127.0.0.1:8000/', true );
  xmlHttp.onload = function () {
    console.log('rsrs');
  };
  xmlHttp.send( null );
  
  source.addEventListener("update", function(event) {
    console.log('rsrs ', event);
  });
  source.addEventListener("end", function(event) {
      console.log('Handling end....')
      source.close(); 
  });

  return <>Oi</>
}

export default App;
