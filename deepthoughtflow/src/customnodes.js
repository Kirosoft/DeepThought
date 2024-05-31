import {LiteGraph} from 'litegraph.js';


LiteGraph.clearRegisteredTypes();

import {AgentNode, UserInput} from './nodes/agentnode.js'
import {ContextNode} from './nodes/contextnode.js'
import {TestWidgetsNode} from './nodes/testwidget.js'
import {Subgraph, GraphInput, GraphOutput} from './nodes/subgraph.js'



LiteGraph.registerNodeType("agents/Basic", AgentNode );
LiteGraph.registerNodeType("agents/UserInput", UserInput );
LiteGraph.registerNodeType("agents/ContextNode", ContextNode );

LiteGraph.registerNodeType("features/widgets", TestWidgetsNode );
LiteGraph.registerNodeType("graph/group", Subgraph );
LiteGraph.registerNodeType("graph/input", GraphInput );
LiteGraph.registerNodeType("graph/output", GraphOutput );

//Constant
function Time() {
	this.addOutput("in ms", "number");
	this.addOutput("in sec", "number");
}

Time.title = "Time";
Time.desc = "Time";

Time.prototype.onExecute = function() {
	this.setOutputData(0, this.graph.globaltime * 1000);
	this.setOutputData(1, this.graph.globaltime);
};

LiteGraph.registerNodeType("basic/time", Time);

//to store json objects
function JSONParse() {
	this.addInput("parse", LiteGraph.ACTION);
	this.addInput("json", "string");
	this.addOutput("done", LiteGraph.EVENT);
	this.addOutput("object", "object");
	this.widget = this.addWidget("button","parse","",this.parse.bind(this));
	this._str = null;
	this._obj = null;
}

JSONParse.title = "JSON Parse";
JSONParse.desc = "Parses JSON String into object";

JSONParse.prototype.parse = function()
{
	if(!this._str)
		return;

	try {
		this._str = this.getInputData(1);
		this._obj = JSON.parse(this._str);
		this.boxcolor = "#AEA";
		this.triggerSlot(0);
	} catch (err) {
		this.boxcolor = "red";
	}
}

JSONParse.prototype.onExecute = function() {
	this._str = this.getInputData(1);
	this.setOutputData(1, this._obj);
};

JSONParse.prototype.onAction = function(name) {
	if(name == "parse")
		this.parse();
}

LiteGraph.registerNodeType("basic/jsonparse", JSONParse);	

//Show value inside the debug console
function TimerEvent() {
	this.addProperty("interval", 1000);
	this.addProperty("event", "tick");
	this.addOutput("on_tick", LiteGraph.EVENT);
	this.time = 0;
	this.last_interval = 1000;
	this.triggered = false;
}

TimerEvent.title = "Timer";
TimerEvent.desc = "Sends an event every N milliseconds";

TimerEvent.prototype.onStart = function() {
	this.time = 0;
};

TimerEvent.prototype.getTitle = function() {
	return "Timer: " + this.last_interval.toString() + "ms";
};

TimerEvent.on_color = "#AAA";
TimerEvent.off_color = "#222";

TimerEvent.prototype.onDrawBackground = function() {
	this.boxcolor = this.triggered
		? TimerEvent.on_color
		: TimerEvent.off_color;
	this.triggered = false;
};

TimerEvent.prototype.onExecute = function() {
	var dt = this.graph.elapsed_time * 1000; //in ms

	var trigger = this.time == 0;

	this.time += dt;
	this.last_interval = Math.max(
		1,
		this.getInputOrProperty("interval") | 0
	);

	if (
		!trigger &&
		(this.time < this.last_interval || isNaN(this.last_interval))
	) {
		if (this.inputs && this.inputs.length > 1 && this.inputs[1]) {
			this.setOutputData(1, false);
		}
		return;
	}

	this.triggered = true;
	this.time = this.time % this.last_interval;
	this.trigger("on_tick", this.properties.event);
	if (this.inputs && this.inputs.length > 1 && this.inputs[1]) {
		this.setOutputData(1, true);
	}
};

TimerEvent.prototype.onGetInputs = function() {
	return [["interval", "number"]];
};

TimerEvent.prototype.onGetOutputs = function() {
	return [["tick", "boolean"]];
};

LiteGraph.registerNodeType("events/timer", TimerEvent);




