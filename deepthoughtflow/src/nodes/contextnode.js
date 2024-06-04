import {LGraphNode} from 'litegraph.js';
import {DTAI} from '../dtai/dtai-core'

require("whatwg-fetch");

var dtai = new DTAI();



export class ContextNode  extends LGraphNode {

    constructor() {
        super();
        this.initIO();
        this.size = this.computeSize();
        this.serialize_widgets = true;
        // this.title = this.properties.name;
        //this.properties = this.constructor.properties;
    }

    initWidgets() {
        var _this = this;

        this.name = this.addWidget("text", "Name", this.properties.name, function(v) {}, { multiline: true, property: "name" });
        this.loader = this.addWidget("text", "Loader", this.properties.loader, function(v) {}, { multiline: true, property: "loader" });
        this.loader_args_url = this.addWidget("text", "URL", this.properties.loader_args_url, function(v) {}, { multiline: true, property: "loader_args_url" });
        this.save = this.addWidget("button", "Save Context", "default", async function(v) { 
            console.log("save context");
            _this.properties.name = _this.title;
            var res = await dtai.saveContext(JSON.stringify(_this.properties))

            console.log(res);
        });
        this.test_role = this.addWidget("button", "Refresh Context", "default", async function(v) { 
            console.log("Refresh started");
            _this.properties.name = _this.title;

            // TODO: maybe save here?
        });
    }

    initIO() {
        this.addInput("Trigger", "text");
        this.addOutput("Context", "text");
    }

    onAdded() {
        console.log('on load');
        this.initWidgets();
    }

    onExecute() {
        const data = this.getInputData(0);
        console.log('on execute');
    }

    computeSize() {
        var size = super.computeSize();
        size[0] += 150;
        return size;
    }
}

