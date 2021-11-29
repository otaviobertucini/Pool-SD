import React, { useState } from "react";

let HAS_LOADED = false;

export default function Main() {
  // let source = null;
  const [source, setSource] = useState(null);
  const [name, setName] = useState(null);

  function start() {
    let new_source = new EventSource("http://127.0.0.1:8000/poll");
    setSource(new_source);

    new_source.addEventListener("message", (event) => {

      const { type, data } = JSON.parse(event.data);
      let logger = document.getElementById("eventLog");

      if (type === 'register') {

        logger.innerHTML += `<p>O usuário ${data.name} foi cadastrado</p>`

        return
      }

      if (type === 'closedPoll') {
        logger.innerHTML += `<p>${data.message}</p>`

        return
      }

      if (type === 'new_event') {
        logger.innerHTML += `<p>O usuário ${data.username} criou a enquete '${data.name}'</p>`

        return
      }

    });
  }

  function cadastrar() {
    const input_name = document.getElementById("name").value;
    setName(input_name);

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "http://127.0.0.1:8000/client", true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      start();

      window.addEventListener("beforeunload", function (e) {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open(
          "POST",
          `http://127.0.0.1:8000/close?username=${input_name}`,
          true
        );
        xmlHttp.send();
        alert('ta fechando essa loca')
        e.preventDefault();
        e.returnValue = "";
      });
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
    xmlHttp.open("POST", `http://127.0.0.1:8000/event`, true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      // console.log(event);
    };
    xmlHttp.send(
      JSON.stringify({
        username: name,
        name: eventName,
        place: eventPlace,
        suggestions: eventSuggestions,
        due_date: evenDueDate,
      })
    );
  }

  function Votar() {
    const eventName = document.getElementById("voteEventName").value;
    // const chosenDate = document.getElementById("chosenDate").value;
    const chosenDate = document.querySelector(
      'input[name="suggestion"]:checked'
    ).value;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", `http://127.0.0.1:8000/vote`, true);
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {

      console.log('votei: ', event);
      const { error, message } = JSON.parse(event.target.response);

      if (error) {
        alert(`Erro: ${message}`)
      } else {
        alert(message)
      }

      const radio_form = document.getElementById("radio_form");

      radio_form.innerHTML = '';

    };
    xmlHttp.send(
      JSON.stringify({
        username: name,
        name: eventName,
        chosenDate: chosenDate,
      })
    );
  }

  function fetchEvent() {
    const eventName = document.getElementById("voteEventName").value;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open(
      "GET",
      `http://127.0.0.1:8000/suggestions?name=${eventName}`,
      true
    );
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {
      // console.log(event);

      const { error, data, message } = JSON.parse(event.target.response);

      if (error) {
        alert(message)
        return
      }

      const radio_form = document.getElementById("radio_form");
      let append = "";
      data.forEach((suggestion, index) => {
        append += `<br><label><input type="radio" name="suggestion" value=${index + 1
          } />${suggestion}</label></br>`;
      });

      radio_form.innerHTML = append;
    };
    xmlHttp.send();
  }

  function consultEvent() {
    const eventName = document.getElementById("verifyEventName").value;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open(
      "GET",
      `http://127.0.0.1:8000/details?name=${eventName}&username=${name}`,
      true
    );
    xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    xmlHttp.onload = function (event) {

      const { data, error, message } = JSON.parse(event.target.response);

      const verifyResult = document.getElementById("verifyResult");


      var votes = 0;
      data.voteCount.forEach((vote, index) => {
        votes += data.voteCount[index]
      })

      let suggestions = ''
      data.suggestions.forEach((suggestion, index) => {
        suggestions += `<br>${suggestion} tem ${data.voteCount[index]} votos</br>`
      })

      let subs = "";
      data.subscribers.forEach((subscriber, index) => {
        subs += `${subscriber}, `
      })


      verifyResult.innerHTML = `<br>Consulta realizada com sucesso:</br>
                                <br>Evento "${data.name}" possui ${votes} votos</br>
                                <br>${data.opened ? "Enquete andamento" : "Enquete encerrada"}</br>
                                ${suggestions}
                                <br>Usuários inscritos/votantes: ${subs}</br>`;

    };
    xmlHttp.send();
  }

  return (
    <div>
      {name ? (
        <>
          <div>Painel do user: {name}</div>
          <div id="eventLog"></div>
          <div id="cadastrar_evento">
            <h1>Aqui tu cadastra evento</h1>
            <p>
              Nome da enquete
              <input id="eventName" defaultValue="evento"></input>
            </p>
            <p>
              Local da enquete
              <input id="eventPlace" defaultValue="daily"></input>
            </p>
            <p>
              Horários
              <input
                id="eventSuggestions"
                defaultValue="05/11/2021 10:00:00, 05/11/2021 11:00:00, 05/11/2021 12:00:00, 05/11/2021 13:00:00"
              ></input>
            </p>
            <p>
              Data final
              <input id="evenDueDate" defaultValue="02/12/2021 14:30:00"></input>
            </p>
            <p>
              <button
                onClick={() => {
                  cadastrarEvento();
                }}
              >
                Cadastrar evento
              </button>
            </p>
          </div>
          <div>
            <h1>Aqui tu vota nos eventos disponíveis</h1>
            Nome do evento
            <input id="voteEventName" defaultValue="evento"></input>
            <div id="eventDetail"></div>
            <p>
              <button
                onClick={() => {
                  fetchEvent();
                }}
              >
                Consultar{" "}
              </button>
            </p>
            <form id="radio_form">
            </form>
            <button
              onClick={() => {
                Votar();
              }}
            >
              Votar
            </button>
          </div>
          <div>
            <h1>Aqui tu verifica o andamento dos eventos disponíveis</h1>
            Nome do evento
            <input id="verifyEventName" defaultValue="evento"></input>
            <div id="verifyResult"></div>
            <p>
              <button
                onClick={() => {
                  consultEvent();
                }}
              >
                Verificar{" "}
              </button>
            </p>
          </div>
        </>
      ) : (
        <>
          Digite o seu nome
          <form>
            <input id="name"></input>
            <button
              onClick={() => {
                cadastrar();
              }}
              type="submit"
            >
              Cadastrar
            </button>
          </form>
        </>
      )}
    </div>
  );
}
