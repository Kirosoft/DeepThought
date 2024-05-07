import { LGraphNode, LiteGraph } from "litegraph.js";

export class TestWidgetsNode extends LGraphNode {

    constructor() {
        super();
        this.properties = {};
        this.title = "Widgets"
        this.initWidgets();
        this.serialize_widgets = true;
    }

    initWidgets() {
        this.slider = this.addWidget("slider", "Slider", 0.5, v => {}, { min: 0, max: 1 });
        this.number = this.addWidget("number", "Number", 0.5, v => {}, { min: 0, max: 100 });
        this.combo = this.addWidget("combo", "Combo", "red", v => {}, { values: ["red", "green", "blue"] });
        this.text = this.addWidget("text", "Text", "edit me", v => {}, {});
        this.text2 = this.addWidget("text", "Text", "multiline", v => {}, { multiline: true });
        this.toggle = this.addWidget("toggle", "Toggle", true, v => {}, { on: "enabled", off: "disabled" });
        this.button = this.addWidget("button", "Button", null, v => {}, {});
        this.toggle2 = this.addWidget("toggle", "Disabled", true, v => {}, { on: "enabled", off: "disabled" });
        this.toggle2.disabled = true;
    }
}


