import {LGraph, LiteGraph, LGraphCanvas} from 'litegraph.js';
import {Editor} from './litegraph-editor.js'
import {} from './customnodes.js'

LiteGraph.node_images_path = "../nodes_data/";

var editor = new LiteGraph.Editor("main",{miniwindow:false});
window.graphcanvas = editor.graphcanvas;
window.graph = editor.graph;
require("whatwg-fetch");

const flowsFunctionUrl = 'http://localhost:7071/api/flows';
const authFunctionUrl = 'http://localhost:7071/api/request_auth';

const authRequestOptions = {
    method: 'GET',  // or 'GET' if no data needs to be sent
    headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'x-user-id': '12345',
        'x-password': 'my_password'
        }
};

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

//create scene selector
var elem = document.createElement("span");
elem.id = "LGEditorTopBarSelector";
elem.className = "selector";
elem.innerHTML = "";
elem.innerHTML += "DeepThoughtFlow <select><option>Empty</option></select> <button class='btn' id='save'>Save</button><button class='btn' id='load'>Load</button> | <button class='btn' id='multiview'>Multiview</button>";
editor.tools.appendChild(elem);

var select = elem.querySelector("select");

select.addEventListener("change", function(e){
	var option = this.options[this.selectedIndex];
	var url = option.dataset["url"];
	
	if(url)
		graph.load( url );
	else if(option.callback)
		option.callback();
	else
		graph.clear();
});

// Set up the request options, including the Authorization header
const saveFlowOptions = {
    method: 'POST',  // or 'GET' if no data needs to be sent
    headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': null,  // Include the API token in the Authorization header
        'x-user-id': '12345'
    }
};


elem.querySelector("#save").addEventListener("click",function(){
	console.log("saved");
	//localStorage.setItem( "graphdemo_save", JSON.stringify( graph.serialize() ) );

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

			saveFlowOptions["headers"]["Authorization"] = `Bearer ${token["token"]}`;
			var body = graph.serialize()
			body["name"]="test_flow"
			saveFlowOptions["body"] = JSON.stringify(body);

			// Make the request

			fetch(flowsFunctionUrl, saveFlowOptions)
				.then(response => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}

					return response.json(); // or response.text() if the response is not in JSON format
				})
				.then(data => {
					console.log('Function responded with:', data);
					graph.configure( data );
					console.log("saved");
				})
				.catch(error => console.error('Failed to fetch:', error));
		})
		.catch(error => console.error('Failed to fetch:', error));

});




// Set up the request options, including the Authorization header
const loadFlowOptions = {
    method: 'GET',  // or 'GET' if no data needs to be sent
    headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': null,  // Include the API token in the Authorization header
        'x-user-id': '12345'
    }
};


elem.querySelector("#load").addEventListener("click",function(){
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

			loadFlowOptions["headers"]["Authorization"] = `Bearer ${token["token"]}`;

			// Make the request

			fetch(flowsFunctionUrl+"?"+new URLSearchParams({id:"test_flow"}), loadFlowOptions)
				.then(response => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}

					return response.json(); // or response.text() if the response is not in JSON format
				})
				.then(data => {
					console.log('Function responded with:', data);
					graph.configure( data );
					console.log("loaded");
				})
				.catch(error => console.error('Failed to fetch:', error));
		})
		.catch(error => console.error('Failed to fetch:', error));



	// var data = localStorage.getItem( "graphdemo_save" );
	// if(data)
	// 	graph.configure( JSON.parse( data ) );
	// console.log("loaded");
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
