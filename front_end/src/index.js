// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/**
 * This file hooks up the "Send" and "Receive" buttons on the web page to the
 * "sendEvents.js" and "receiveEvents.js" samples.
 */
const { send } = require("./send");
const { receive } = require("./receive");

const sendElement = document.getElementById("send");
const receiveElement = document.getElementById("receive");

sendElement.addEventListener("click", () => {
  send();
});

receiveElement.addEventListener("click", () => {
  receive();
});