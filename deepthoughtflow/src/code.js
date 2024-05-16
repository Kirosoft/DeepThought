import {LGraph, LiteGraph, LGraphCanvas} from 'litegraph.js';
import {Editor} from './litegraph-editor.js'
import {} from './customnodes.js'
import { DTAI } from './dtai/dtai-core.js';

LiteGraph.node_images_path = "../nodes_data/";

var editor = new LiteGraph.Editor("main",{miniwindow:false});
window.graphcanvas = editor.graphcanvas;
window.graph = editor.graph;


updateEditorHiPPICanvas();

window.addEventListener("resize", function() { 
  editor.graphcanvas.resize();
  updateEditorHiPPICanvas();
} );

window.onbeforeunload = function(){
	var data = JSON.stringify( graph.serialize() );
	localStorage.setItem("litegraphg demo backup", data );
}

function updateEditorHiPPICanvas() {
  const ratio = window.devicePixelRatio;
  if(ratio == 1) { return }
  const rect = editor.canvas.parentNode.getBoundingClientRect();
  const { width, height } = rect;
  editor.canvas.width = width * ratio;
  editor.canvas.height = height * ratio;
  editor.canvas.style.width = width + "px";
  editor.canvas.style.height = height + "px";
  editor.canvas.getContext("2d").scale(ratio, ratio);
  return editor.canvas;
}

//enable scripting
LiteGraph.allow_scripts = true;

var dtai = new DTAI();

//create scene selector
var elem = document.createElement("span");
elem.id = "LGEditorTopBarSelector";
elem.className = "selector";
elem.innerHTML = "";
elem.innerHTML += "DeepThoughtFlow <select><option>Empty</option></select> <button class='btn' id='save'>Save</button><button class='btn' id='load'>Load</button> | <button class='btn' id='multiview'>Multiview</button>";
editor.tools.appendChild(elem);

var select = elem.querySelector("select");

select.addEventListener("change", async function(e){
	var option = this.options[this.selectedIndex];
	var url = option.dataset["url"];
	
	if(url) {
		await dtai.loadFlow("test_flow").then(flow => {
			graph.configure(flow);
			console.log("loaded");
		}).catch(error => {
			console.log("Error loading flow: ",error);
		});
	
	}
	else if(option.callback)
		option.callback();
	else
		graph.clear();
});



elem.querySelector("#save").addEventListener("click",async () => {

	var flowData = graph.serialize();
	flowData["name"]="test_flow"

	await dtai.saveFlow(JSON.stringify(flowData)).then(result => {
		console.log("saved");
	}).catch(error => {
		console.log("save error");
	});
});



elem.querySelector("#load").addEventListener("click",async () => {
	
	
	await dtai.loadFlow("test_flow").then(flow => {
		graph.configure(flow);
		console.log("loaded");
	}).catch(error => {
		console.log("Error loading flow: ",error);
	});
});



elem.querySelector("#multiview").addEventListener("click", function(){ editor.addMultiview()  } );

function addDemo( name, url )
{
	var option = document.createElement("option");
	if(url.constructor === String)
		option.dataset["url"] = url;
	else
		option.callback = url;
	option.innerHTML = name;
	select.appendChild( option );
}

//some examples
addDemo("Features", "examples/features.json");
addDemo("Benchmark", "examples/benchmark.json");
addDemo("Subgraph", "examples/subgraph.json");
addDemo("test_flow", "test_flow");
