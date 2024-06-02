import {LGraphNode} from 'litegraph.js';
import {DTAI} from '../dtai/dtai-core'

require("whatwg-fetch");

var dtai = new DTAI();



export class AgentNode  extends LGraphNode {

    constructor() {
        super();
        this.properties = { 
            name:"test_role",
            role:"You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
            expected_input:"a question about a UKHO policy",
            expected_output:"a detailed and specific job posting ",
            output_format:[],
            examples:["Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"],
            tools:[],
            options:
            {
                "rag_mode":true
            },
            input: "what are the usability standards",
            answer: "",
            session_token:""
        };

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

    }

    computeSize() {
        var size = super.computeSize();
        size[0] += 150;
        return size;
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

