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

  function cadastrarEvento() {}

  return (
    <div>
      {name ? (
        <>
          <div>Painel do user: {name}</div>
          <div id="main"></div>
          <div id="cadastrar_evento">
            <h1>Aqui tu cadastra evento</h1>
            Nome da enquete
            <input id="event_name" value="evento"></input>
            Local da enquete
            <input id="event_place" value="daily"></input>
            Horários
            <input id="event_suggestions" value="05/11/2021 10:00:00, 05/11/2021 11:00:00, 05/11/2021 12:00:00, 05/11/2021 13:00:00"></input>
            Data final
            <input id="event_due_date" value="03/11/2021 14:30:00"></input>
            <button
              onClick={() => {
                cadastrarEvento();
              }}
            >
              Cadastrar evento
            </button>
          </div>
          <div>
            <h1>Aqui tu vê os eventos disponíveis</h1>
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
