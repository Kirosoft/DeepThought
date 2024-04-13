// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/*
  This sample demonstrates how the send() function can be used to send events to Event Hubs.
  See https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-about to learn about Event Hubs.
*/

const { EventHubProducerClient } = require("@azure/event-hubs");
const { AzureSASCredential, AzureNamedKeyCredential } = require("@azure/core-auth");
const { generateSharedAccessSignature, AzureKeyCredential, EventGridPublisherClient } = require("@azure/eventgrid");
const crypto = require('crypto');

const {
  eventHubName,
  connectionString,
  fullyQualifiedNamespace
} = require("./configuration");

const contentContainer = document.getElementById("sendContent");
function outputLog(text) {
  const currentContent = contentContainer.value;
  contentContainer.value = `${currentContent}${text}\n`;
  console.log(text);
}

// Create a SAS Token which expires on 2020-01-01 at Midnight.
const token = generateSharedAccessSignature(
  "deepthought.uksouth-1.eventgrid.azure.net",
  new AzureKeyCredential("9cFtzPq56X3SYeYcNFVaWgyu4TQW2RevLVGrnjCJSO4="),
  new Date("2020-01-01T00:00:00")
);


function createSharedAccessToken(uri, saName, saKey) { 
  if (!uri || !saName || !saKey) { 
          throw "Missing required parameter"; 
      } 
  var encoded = encodeURIComponent(uri); 
  var now = new Date(); 
  var week = 60*60*24*7;
  var ttl = Math.round(now.getTime() / 1000) + week;
  var signature = encoded + '\n' + ttl; 
  var hash = crypto.createHmac('sha256', saKey).update(signature, 'utf8').digest('base64'); 
  return 'SharedAccessSignature sr=' + encoded + '&sig=' +  
      encodeURIComponent(hash) + '&se=' + ttl + '&skn=' + saName; 
}


async function send_eventgrid() {

  // var token = createSharedAccessToken(fullyQualifiedNamespace, "RootManageSharedAccessKey","JUectEsS1vEKno+u9CazZAtKRLrGIqZBi+AEhCJax/k=");
  const client = new EventGridPublisherClient("deepthought.uksouth-1.eventgrid.azure.net","CloudEvent",token);

  await client.send([
    {
      topic: "Core",
      eventType: "Azure.Sdk.SampleEvent",
      subject: "Event Subject",
      dataVersion: "1.0",
      data: {
        hello: "world",
      },
    },
  ]);

  console.log("ok");
}

module.exports = {
  send_eventgrid
};