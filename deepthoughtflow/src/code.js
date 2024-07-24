import '../imgs/load-progress-empty.png'
import '../imgs/load-progress-full.png'
import '../imgs/grid.png'

import '../css/style.css'
import '../css/litegraph-editor.css'
import '../css/litegraph.css'

import {LGraph, LiteGraph, LGraphCanvas} from 'litegraph.js';
import {Editor} from './litegraph-editor.js'
import {} from './customnodes.js'
import { DTAI } from './dtai/dtai-core.js';
import {AgentNode} from './nodes/agentnode.js'
import {ContextNode} from './nodes/contextnode.js'

LiteGraph.node_images_path = "../nodes_data/";

var editor = new Editor("main",{miniwindow:false});
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

// Create scene selector
var elem = document.createElement("span");
elem.id = "LGEditorTopBarSelector";
elem.className = "selector";
elem.innerHTML = "DeepThoughtFlow <select id='sceneSelect'><option>New Flow</option></select> <button class='btn' id='save'>Save</button> <button class='btn' id='delete'>Delete</button> | <button class='btn' id='multiview'>Multiview</button>";
editor.tools.appendChild(elem);

var select = elem.querySelector("#sceneSelect");

// Function to replace select with an input field
function replaceSelectWithInput() {
    var input = document.createElement("input");
    input.type = "text";
    input.id = "editableOption";
    input.placeholder = "Flow name";
    select.parentNode.replaceChild(input, select);
    input.focus();

    // Event to handle when user presses enter in input
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            var newOption = document.createElement("option");
            newOption.text = input.value;
            newOption.selected = true;
            select.appendChild(newOption);
            input.parentNode.replaceChild(select, input); // Switch back to select
			graph.clear();
        }
    });
}

select.addEventListener("change", async function(e) {
    var option = this.options[this.selectedIndex];
    if (option.textContent === "New Flow") {
        replaceSelectWithInput();
    } else {
		await dtai.loadFlow(option.textContent).then(flow => {
			graph.configure(flow);
			console.log("loaded");
		}).catch(error => {
			console.log("Error loading flow: ",error);
		});
	}
});



elem.querySelector("#save").addEventListener("click",async () => {

	var flowData = graph.serialize();
	var selectedText = select.options[select.selectedIndex].text;

	flowData["name"]=selectedText;

	await dtai.saveFlow(JSON.stringify(flowData)).then(result => {
		console.log(`saved ${selectedText}`);
	}).catch(error => {
		console.log("save error");
	});
});



// elem.querySelector("#load").addEventListener("click",async () => {
	
	
// 	await dtai.loadFlow("test_flow").then(flow => {
// 		graph.configure(flow);
// 		console.log("loaded");
// 	}).catch(error => {
// 		console.log("Error loading flow: ",error);
// 	});
// });



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


await  dtai.loadFlows().then(flows => {
	flows?.forEach(flow => {
		console.log(`found flow: ${flow.name}`);
		addDemo(flow.name, flow.name);
	});
});


function createAgentDerivedClass(className) {
    var DynamicClass =  class extends AgentNode {
        constructor() {
            super();
			this.title = className;
        }
    };

	// Set the name of the class dynamically using Object.defineProperty
	Object.defineProperty(DynamicClass, 'name', { value: className });
	// Object.defineProperty(DynamicClass, 'type', { value: className });
	Object.defineProperty(DynamicClass, 'title', { value: className });
	return DynamicClass;
}

function createContextDerivedClass(context) {
    var DynamicClass =  class extends ContextNode {
        constructor() {
            super();
			this.title = context.name;
			this.properties = {
				name: context.name
				// loader:context.loader, 
				// loader_args_url:context.loader_args.url
			};
        }
    };

	// Set the name of the class dynamically using Object.defineProperty
	Object.defineProperty(DynamicClass, 'name', { value: context.name });
	// Object.defineProperty(DynamicClass, 'type', { value: className });
	Object.defineProperty(DynamicClass, 'title', { value: context.name});

	return DynamicClass;
}

await  dtai.loadRoles().then(roles => {

	roles?.user_roles?.forEach(role => {
		console.log(`found user role: ${role.name}`);

		var roleClass = createAgentDerivedClass(role.name);

		LiteGraph.registerNodeType(`roles/${role.name}`, roleClass);

	});

	roles?.system_roles?.forEach(role => {
		console.log(`found system role: ${role.name}`);
	});

});

await  dtai.loadContexts().then(contexts => {

	contexts?.user_contexts?.forEach(context => {
		console.log(`found context: ${context.name}`);

		var contextClass = createContextDerivedClass(context);

		LiteGraph.registerNodeType(`contexts/${context.name}`, contextClass);

	});
});

