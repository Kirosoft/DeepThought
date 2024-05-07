import {LiteGraph, LGraphNode} from 'litegraph.js';


export class Subgraph  extends LGraphNode {

    constructor() {
        super();
        this.size = [140, 80];
        this.properties = { enabled: true };
        this.enabled = true;

        this.title = "Subgraph";
        this.desc = "Graph inside a node";
        this.title_color = "#334";
    
        // Create inner graph
        this.subgraph = new LiteGraph.LGraph();
        this.subgraph._subgraph_node = this;
        this.subgraph._is_subgraph = true;

        var that = this;
        
        // Bind event handlers
        this.subgraph.onTrigger = this.onSubgraphTrigger.bind(that);
        this.subgraph.onInputAdded = this.onSubgraphNewInput.bind(that);
        this.subgraph.onInputRenamed = this.onSubgraphRenamedInput.bind(that);
        this.subgraph.onInputTypeChanged = this.onSubgraphTypeChangeInput.bind(that);
        this.subgraph.onInputRemoved = this.onSubgraphRemovedInput.bind(that);
        this.subgraph.onOutputAdded = this.onSubgraphNewOutput.bind(that);
        this.subgraph.onOutputRenamed = this.onSubgraphRenamedOutput.bind(that);
        this.subgraph.onOutputTypeChanged = this.onSubgraphTypeChangeOutput.bind(that);
        this.subgraph.onOutputRemoved = this.onSubgraphRemovedOutput.bind(that);
    }

    onSubgraphTrigger(event, param) {
        const slot = this.findOutputSlot(event);
        if (slot !== -1) {
            this.triggerSlot(slot, param);
        }
    }

    onSubgraphNewInput(name, type) {
        const slot = this.findInputSlot(name);
        if (slot === -1) {
            this.addInput(name, type);
        }
    }

    onSubgraphRenamedInput(oldname, name) {
        const slot = this.findInputSlot(oldname);
        if (slot !== -1) {
            const info = this.getInputInfo(slot);
            info.name = name;
        }
    }

    onSubgraphTypeChangeInput(name, type) {
        const slot = this.findInputSlot(name);
        if (slot !== -1) {
            const info = this.getInputInfo(slot);
            info.type = type;
        }
    }

    onSubgraphRemovedInput(name) {
        const slot = this.findInputSlot(name);
        if (slot !== -1) {
            this.removeInput(slot);
        }
    }

    onSubgraphNewOutput(name, type) {
        const slot = this.findOutputSlot(name);
        if (slot === -1) {
            this.addOutput(name, type);
        }
    }

    onSubgraphRenamedOutput(oldname, name) {
        const slot = this.findOutputSlot(oldname);
        if (slot !== -1) {
            const info = this.getOutputInfo(slot);
            info.name = name;
        }
    }

    onSubgraphTypeChangeOutput(name, type) {
        const slot = this.findOutputSlot(name);
        if (slot !== -1) {
            const info = this.getOutputInfo(slot);
            info.type = type;
        }
    }

    onSubgraphRemovedOutput(name) {
        const slot = this.findOutputSlot(name);
        if (slot !== -1) {
            this.removeOutput(slot);
        }
    }

    serialize = function() {
        var data = LiteGraph.LGraphNode.prototype.serialize.call(this);
        data.subgraph = this.subgraph.serialize();
        return data;
    };

    // Additional methods (such as onDblClick, onExecute, etc.) would continue below with similar refactoring.
}

export class GraphInput  extends LGraphNode {

    constructor() {
        super();
        this.addOutput("", "number");
        this.name_in_graph = "";
        this.title = "Input";
        this.desc = "Input of the graph";
    
        this.properties = {
            name: "",
            type: "number",
            value: 0
        };

        // Setup widgets with arrow functions to maintain 'this' context
        this.name_widget = this.addWidget("text", "Name", this.properties.name, (v) => {
            if (!v) return;
            this.setProperty("name", v);
        });

        this.type_widget = this.addWidget("text", "Type", this.properties.type, (v) => {
            this.setProperty("type", v);
        });

        this.value_widget = this.addWidget("number", "Value", this.properties.value, (v) => {
            this.setProperty("value", v);
        });

        this.widgets_up = true;
        this.size = [180, 90];
    }

    // Methods to handle widget interactions and updates
    setProperty(name, value) {
        this.properties[name] = value;
        this.onPropertyChanged(name, value);
    }

    onConfigure() {
        this.updateType();
    }

    updateType() {
        const type = this.properties.type;
        this.type_widget.value = type;

        // Update output
        if (this.outputs[0].type !== type) {
            if (!LiteGraph.isValidConnection(this.outputs[0].type, type))
                this.disconnectOutput(0);
            this.outputs[0].type = type;
        }

        // Update widget based on type
        if (type === "number") {
            this.value_widget.type = "number";
            this.value_widget.value = 0;
        } else if (type === "boolean") {
            this.value_widget.type = "toggle";
            this.value_widget.value = true;
        } else if (type === "string") {
            this.value_widget.type = "text";
            this.value_widget.value = "";
        } else {
            this.value_widget.type = null;
            this.value_widget.value = null;
        }
        this.properties.value = this.value_widget.value;

        // Update graph if needed
        if (this.graph && this.name_in_graph) {
            this.graph.changeInputType(this.name_in_graph, type);
        }
    }

    onPropertyChanged(name, value) {
        if (name === "name") {
            if (value === "" || value === this.name_in_graph || value === "enabled") {
                return false;
            }
            if (this.graph) {
                if (this.name_in_graph) {
                    this.graph.renameInput(this.name_in_graph, value);
                } else {
                    this.graph.addInput(value, this.properties.type);
                }
            }
            this.name_widget.value = value;
            this.name_in_graph = value;
        } else if (name === "type") {
            this.updateType();
        } else if (name === "value") {
            // Additional actions if needed when value changes
        }
    }

    getTitle() {
        if (this.flags && this.flags.collapsed) {
            return this.properties.name;
        }
        return this.constructor.title; // Accessing static property using constructor
    }

    onAction(action, param) {
        if (this.properties.type === LiteGraph.EVENT) {
            this.triggerSlot(0, param);
        }
    }

    onExecute() {
        const name = this.properties.name;
        const data = this.graph ? this.graph.inputs[name] : null;
        this.setOutputData(0, data && data.value !== undefined ? data.value : this.properties.value);
    }

    onRemoved() {
        if (this.name_in_graph && this.graph) {
            this.graph.removeInput(this.name_in_graph);
        }
    }
}

export class GraphOutput extends LGraphNode {
    constructor() {
        super();
        this.addInput("", "number");
        this.name_in_graph = "";
        this.title = "GraphOutput";
        this.desc = "Ouput of the graph";
    
        this.properties = {
            name: "",
            type: "number",
            value: 0
        };

        // Setup widgets with arrow functions to maintain 'this' context
        this.name_widget = this.addWidget("text", "Name", this.properties.name, (v) => {
            if (!v) return;
            this.setProperty("name", v);
        });

        this.type_widget = this.addWidget("text", "Type", this.properties.type, (v) => {
            this.setProperty("type", v);
        });

        this.value_widget = this.addWidget("number", "Value", this.properties.value, (v) => {
            this.setProperty("value", v);
        });

        this.widgets_up = true;
        this.size = [180, 90];
    }

    // Methods to handle widget interactions and updates
    setProperty(name, value) {
        this.properties[name] = value;
        this.onPropertyChanged(name, value);
    }

    onConfigure() {
        this.updateType();
    }

    updateType() {
        const type = this.properties.type;
        this.type_widget.value = type;

        // Update input
        if (this.inputs[0].type !== type) {
            if (!LiteGraph.isValidConnection(this.inputs[0].type, type))
                this.disconnectInput(0);
            this.inputs[0].type = type;
        }

        // Update widget based on type
        if (type === "number") {
            this.value_widget.type = "number";
            this.value_widget.value = 0;
        } else if (type === "boolean") {
            this.value_widget.type = "toggle";
            this.value_widget.value = true;
        } else if (type === "string") {
            this.value_widget.type = "text";
            this.value_widget.value = "";
        } else {
            this.value_widget.type = null;
            this.value_widget.value = null;
        }
        this.properties.value = this.value_widget.value;

        // Update graph if needed
        if (this.graph && this.name_in_graph) {
            this.graph.changeOutputType(this.name_in_graph, type);
        }
    }

    onPropertyChanged(name, value) {
        if (name === "name") {
            if (value === "" || value === this.name_in_graph || value === "enabled") {
                return false;
            }
            if (this.graph) {
                if (this.name_in_graph) {
                    this.graph.renameOutput(this.name_in_graph, value);
                } else {
                    this.graph.addOutput(value, this.properties.type);
                }
            }
            this.name_widget.value = value;
            this.name_in_graph = value;
        } else if (name === "type") {
            this.updateType();
        } else if (name === "value") {
            // Additional actions if needed when value changes
        }
    }

    getTitle() {
        if (this.flags.collapsed) {
            return this.properties.name;
        }
        return this.title;
    }

    onAction(action, param) {
        if (this.properties.type == LiteGraph.ACTION) {
            this.graph.trigger( this.properties.name, param );
        }
    }

    onExecute() {
        this._value = this.getInputData(0);
        this.graph.setOutputData(this.properties.name, this._value);
    }

    onRemoved() {
        if (this.name_in_graph) {
            this.graph.removeOutput(this.name_in_graph);
        }
    }
}

