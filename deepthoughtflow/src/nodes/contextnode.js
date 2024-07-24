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

        this.context_definition = this.addWidget("text", "context definition", this.properties.name, function(v) {}, { multiline: false, property: "name" });
        // this.save = this.addWidget("button", "Save Context", "default", async function(v) { 
        //     console.log("save context");
        //     _this.properties.name = _this.title;
        //     var res = await dtai.saveContext(JSON.stringify(_this.properties))

        //     console.log(res);
        // });
        // this.test_role = this.addWidget("button", "Refresh Context", "default", async function(v) { 
        //     console.log("Refresh started");
        //     _this.properties.name = _this.title;

        //     // TODO: maybe save here?
        // });
    }

    initIO() {
        this.addInput("trigger", "text");
        this.addOutput("context", "text");
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

export class InputNode  extends LGraphNode {

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

    }

    initIO() {
        this.addOutput("ouput", "text");
    }

    onAdded() {
        console.log('on load');
        this.initWidgets();
    }

    onExecute() {
        console.log('on execute');
    }

    computeSize() {
        var size = super.computeSize();
        size[0] += 150;
        return size;
    }
}


export class OutputNode  extends LGraphNode {

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

    }

    initIO() {
        this.addInput("input", "text");
    }

    onAdded() {
        console.log('on load');
        this.initWidgets();
    }

    onExecute() {
        console.log('on execute');
    }

    computeSize() {
        var size = super.computeSize();
        size[0] += 150;
        return size;
    }
}