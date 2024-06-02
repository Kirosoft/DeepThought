import {LGraphNode} from 'litegraph.js';
import {DTAI} from '../dtai/dtai-core'

require("whatwg-fetch");

var dtai = new DTAI();



export class ContextNode  extends LGraphNode {

    constructor() {
        super();
        this.properties = { 
            "id": name,
            "tenant": "ukho",
            "user_id": "12345",
            "data_type": "context_definition",
            "name": name,
            "loader": "pdf_file_loader",
            "loader_args": {
                "url": url,
            },
            "adaptor": "html_to_text",
            "adaptor_args": {},
            "current_version":0,
            "rag_options": {
                "chunk_size": 1000,
                "overlap": 250,
                "strategy": "basic"
            }
        }

        this.initWidgets();
        this.initIO();
        this.size = this.computeSize();
        this.serialize_widgets = true;
        // this.title = this.properties.name;
    }

    initWidgets() {
        var _this = this;

        this.role = this.addWidget("text", "Role", this.properties.role, function(v) {}, { multiline: true, property: "role" });
        this.examples = this.addWidget("text", "Examples", this.properties.examples, function(v) {}, { multiline: true, property: "examples" });
        this.expected_input = this.addWidget("text", "Expected Input", this.properties.expected_input, function(v) {}, { multiline: true, property: "expected_input" });
        this.expected_output = this.addWidget("text", "Expected Output", this.properties.expected_output, function(v) {}, { multiline: true, property: "expected_output" });
        this.output_format = this.addWidget("combo", "Output Format", this.properties.output_format, function(v) {}, { multiline: true, property: "output_format", values: ["", "spec-a","spc-b","spc-c"] });
        this.tools = this.addWidget("Combo", "Tools", this.properties.tools, function(v) {}, { multiline: true, property: "tools", values: ["", "tool-a","tool-b","tool-c"] });
        this.save = this.addWidget("button", "Save Role", "default", async function(v) { 
            console.log("save role started");
            _this.properties.name = _this.title;
            var res = await dtai.saveRole(JSON.stringify(_this.properties))

            console.log(res);
        });
        this.test_role = this.addWidget("button", "Test Role", "default", async function(v) { 
            console.log("test started");
            _this.properties.name = _this.title;

            // TODO: maybe save here?

            var payload = {
                    "input": _this.properties.input,
                    "role": _this.title, 
                    "name":"run_agent"
            }
            var res = await dtai.runAgent(JSON.stringify(payload))
            console.log(res);
            _this.properties.answer=res.answer;
        });
    }

    initIO() {
        this.addInput("Input Request", "text");
        this.addInput("Context", "text");
        this.addInput("Examples", "text");
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

    computeSize() {
        var size = super.computeSize();
        size[0] += 150;
        return size;
    }
}

