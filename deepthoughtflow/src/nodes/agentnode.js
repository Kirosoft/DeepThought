import {LGraphNode} from 'litegraph.js';
require("whatwg-fetch");

const azureFunctionUrl = 'http://localhost:7071/api/core_llm_agent';
const apiToken = 'Bearer YOUR_API_TOKEN';

export class AgentNode  extends LGraphNode {

    constructor() {
        super();
        this.properties = { role: "ukho" };
        this.initWidgets();
        this.initIO();
        this.size = this.computeSize();
        this.serialize_widgets = true;
        this.title = "Agent"
    }

    initWidgets() {
        this.temperature = this.addWidget("slider", "Temperature", 0.5, function(v) {}, { min: 0, max: 1 });
        this.role = this.addWidget("combo", "role", "default", function(v) {}, { values: ["ukho", "lawyer", "researcher"] });
        this.text = this.addWidget("text", "Examples", "multiline", function(v) {}, { multiline: true });
    }

    initIO() {
        this.addInput("Input Request", "text");
        this.addOutput("Answer", "text");
    }

    onExecute() {
        const data = this.getInputData(0);
        var document = {"input": data, "role":"ukho_policy", "name":"core_llm_agent"}

        // Set up the request options, including the Authorization header
        const requestOptions = {
            method: 'POST',  // or 'GET' if no data needs to be sent
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'Authorization': apiToken  // Include the API token in the Authorization header
            },
            body: JSON.stringify(document)
        };

        // Make the request
        fetch(azureFunctionUrl, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // or response.text() if the response is not in JSON format
            })
            .then(data => {
                console.log('Function responded with:', data);

                this.setOutputData(0, data && data.value !== undefined ? data.value : this.properties.value);
            })
            .catch(error => console.error('Failed to fetch:', error));
    }
}

export class UserInput extends LGraphNode {

    constructor() {
        super();
        this.properties = { output: "" };
        this.initWidgets();
        this.initIO();
        this.size = this.computeSize();
        this.serialize_widgets = true;
        this.title = "Agent"
    }

    initWidgets() {
        this.text = this.addWidget("text", "UserInput", "multiline", function(v) {}, { multiline: true });
    }

    initIO() {
        this.addOutput("UserText", "text");
    }

    onExecute() {
        this.setOutputData(0, this.text.value);
        this.properties.output = this.text.value;
    }
}
