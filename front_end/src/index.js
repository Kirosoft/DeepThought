// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/**
 * This file hooks up the "Send" and "Receive" buttons on the web page to the
 * "sendEvents.js" and "receiveEvents.js" samples.
 */
const { send_eventhub } = require("./send_eventhub");
const { receive_eventhub } = require("./receive_eventhub");
const { send_eventgrid } = require("./send_eventgrid");
const { receive_eventgrid } = require("./receive_eventgrid");

const sendElement = document.getElementById("send");
const receiveElement = document.getElementById("receive");

sendElement.addEventListener("click", () => {
  console.log("test send 1")
  send_eventgrid();

});

receiveElement.addEventListener("click", () => {
  receive_eventgrid();
});