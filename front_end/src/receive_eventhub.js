// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

/*
  This sample demonstrates how to use the EventHubConsumerClient to process events from all partitions
  of a consumer group in an Event Hubs instance.

  To start receiving events, click the "Receive" button from the web page.

  If your Event Hub instance doesn't have any events, you can run the "sendEvents.js" sample from
  the web page by clicking the "Send" button.
*/

const { EventHubConsumerClient } = require("@azure/event-hubs");
const { AzureSASCredential, AzureNamedKeyCredential } = require("@azure/core-auth");
const crypto = require('crypto');

const {
  consumerGroup,
  eventHubName,
  fullyQualifiedNamespace,
  connectionString,
} = require("./configuration.js");

const contentContainer = document.getElementById("receiveContent");
function outputLog(text) {
  const currentContent = contentContainer.value;
  contentContainer.value = `${currentContent}${text}\n`;
}

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


async function receive_eventhub() {

  var token = createSharedAccessToken(fullyQualifiedNamespace, "RootManageSharedAccessKey","JUectEsS1vEKno+u9CazZAtKRLrGIqZBi+AEhCJax/k=");
  const consumerClient = new EventHubConsumerClient(consumerGroup, connectionString, eventHubName, new AzureSASCredential(token));


  const partitionIds = await consumerClient.getPartitionIds();
  outputLog(`Preparing to read events from partitions: ${partitionIds.join(", ")}`);

  consumerClient.subscribe(
    {
      // The callback where you add your code to process incoming events
      processEvents: async (events, context) => {
        for (const event of events) {
          outputLog(
            `Received event: '${event.body}' from partition: '${context.partitionId}' and consumer group: '${context.consumerGroup}'`
          );
        }
      },
      processError: async (err) => {
        outputLog(`Error : ${err}`);
      }
    },
    {
      maxWaitTimeInSeconds: 5
    }
  );
}

module.exports = {
  receive_eventhub
};