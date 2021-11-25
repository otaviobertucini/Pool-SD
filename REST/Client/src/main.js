import React, { useState } from "react";

let HAS_LOADED = false;

export default function Main() {
  // let source = null;
  const [source, setSource] = useState(null);
  const [name, setName] = useState(null);

  function start() {
    let new_source = new EventSource("http://127.0.0.1:8000/poll");
    setSource(new_source);

    new_source.addEventListener("new", (event) => {
      document.getElementById("main").append(JSON.stringify(event.data));
    });
  }

  function cadastrar() {
    const input_name = document.getElementById("name").value;
    setName(input_name);

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "http://127.0.0.1:8000/poll", true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      start();
    };
    xmlHttp.send(
      JSON.stringify({
        name: input_name,
      })
    );
  }



  function cadastrarEvento() {

    const eventName = document.getElementById("eventName").value;
    const eventPlace = document.getElementById("eventPlace").value;
    const eventSuggestions = document.getElementById("eventSuggestions").value;
    const evenDueDate = document.getElementById("evenDueDate").value;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "http://127.0.0.1:8000/event", true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      console.log(event)
    };
    xmlHttp.send(
      JSON.stringify({
        username: name,
        name: eventName,
        place: eventPlace,
        suggestions: eventSuggestions,
        due_date: evenDueDate
      })
    );
  }

  function fetchEvent(){

    const eventName = document.getElementById("enquete").value;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", `http://127.0.0.1:8000/details?username=${name}&name=${eventName}`, true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      const { data, error } = JSON.parse(event.target.response);
      
      if(error){
        alert('deu bosta')
        return
      }
      
      const radio_form = document.getElementById('radio_form');
      let append = ''
      console.log(data)
      data.suggestions.forEach((suggestion, index) => {

        append += `<br><label><input type="radio" name="suggestion" value=${index + 1} />${suggestion}</label></br>`

      });

      radio_form.innerHTML = append

      console.log(data);
    };
    xmlHttp.send();

  }

  return (
    <div>
      {name ? (
        <>
          <div>Painel do user: {name}</div>
          <div id="main"></div>
          <div id="cadastrar_evento">
            <h1>Aqui tu cadastra evento</h1>
            <p>Nome da enquete
            <input id="eventName" value="evento"></input></p>
            <p>Local da enquete
            <input id="eventPlace" value="daily"></input></p>
            <p>Horários
            <input id="eventSuggestions" value="05/11/2021 10:00:00, 05/11/2021 11:00:00, 05/11/2021 12:00:00, 05/11/2021 13:00:00"></input></p>
            <p>Data final
            <input id="evenDueDate" value="03/11/2021 14:30:00"></input></p>
            <p><button
              onClick={() => {
                cadastrarEvento();
              }}
            >
              Cadastrar evento
            </button></p>
          </div>
          <div>
            <h1>Aqui tu vê os eventos disponíveis</h1>
            Nome do evento
            <input id="enquete" value="evento"></input>
            <div id="eventDetail"></div>
            <form id="radio_form">
              {/* <label><input type="radio" name="test" value="A"> A</label>
              <label><input type="radio" name="test" value="B" checked> B</label>
              <label><input type="radio" name="test" value="C"> C</label> */}
            </form>
   

            <p><button
              onClick={() => {
                fetchEvent();
              }}
            >
            Consultar </button></p>

          </div>
          {/* <button onClick={() => {}}>Botão</button> */}
        </>
      ) : (
        <>
          Digite o seu nome
          <input id="name"></input>
          <button
            onClick={() => {
              cadastrar();
            }}
          >
            Cadastrar
          </button>
        </>
      )}
    </div>
  );
}
