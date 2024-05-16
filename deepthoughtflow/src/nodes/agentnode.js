import {LGraphNode} from 'litegraph.js';
require("whatwg-fetch");



export class AgentNode  extends LGraphNode {

    constructor() {
        super();
        this.properties = { role: "ukho", answer: "" };
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

        // Make the request
        fetch(authFunctionUrl, authRequestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // or response.text() if the response is not in JSON format
            })
            .then(token => {
                console.log('Function responded with:', token);

                requestOptions["headers"]["Authorization"] = `Bearer ${token["token"]}`;

                // Make the request
                fetch(agentFunctionUrl, requestOptions)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json(); // or response.text() if the response is not in JSON format
                    })
                    .then(data => {
                        console.log('Function responded with:', data);

                        this.setOutputData(0, data && data.value !== undefined ? data.value : this.properties.value);
                        this.properties.answer = data['answer'];
                    })
                    .catch(error => console.error('Failed to fetch:', error));

                this.setOutputData(0, data && data.value !== undefined ? data.value : this.properties.value);
            })
            .catch(error => console.error('Failed to fetch:', error));

        var document = {"input": data, "role":"ukho_policy", "name":"core_llm_agent"}


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
