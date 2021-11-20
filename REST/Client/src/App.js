import React from "react";

let HAS_LOADED = false;

function App() {
  function start() {
    // Subscribe no SSE
    var source = new EventSource("http://127.0.0.1:8000/poll");

    source.addEventListener("new", (event) => {
      console.log("rsrs ", event);
    });
  }

  if (!HAS_LOADED) {
    HAS_LOADED = true;

    const name = prompt("Digite o nome do cliente jahahahahaha");

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "http://127.0.0.1:8000/poll", true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      alert("Deu boa");
      start();
    };
    xmlHttp.send(
      JSON.stringify({
        name,
      })
    );
  }

  return <>Oi</>;
}

export default App;
