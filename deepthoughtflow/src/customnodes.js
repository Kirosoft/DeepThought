import {LiteGraph} from 'litegraph.js';


LiteGraph.clearRegisteredTypes();

import {AgentNode, UserInput} from './nodes/agentnode.js'
import {TestWidgetsNode} from './nodes/testwidget.js'
import {Subgraph, GraphInput, GraphOutput} from './nodes/subgraph.js'




LiteGraph.registerNodeType("agents/Basic", AgentNode );
LiteGraph.registerNodeType("agents/UserInput", UserInput );

LiteGraph.registerNodeType("features/widgets", TestWidgetsNode );


// Subgraph ndoes
LiteGraph.registerNodeType("graph/subgraph", Subgraph);
LiteGraph.GraphInput = GraphInput;
LiteGraph.registerNodeType("graph/input", GraphInput);
LiteGraph.GraphOutput = GraphOutput;
LiteGraph.registerNodeType("graph/output", GraphOutput);


