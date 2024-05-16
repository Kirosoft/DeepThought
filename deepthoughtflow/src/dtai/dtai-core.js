

import {DTAI_User} from "./dtai-user.js";
require("whatwg-fetch");

const flowsFunctionUrl = 'http://localhost:7071/api/flows';

const agentFunctionUrl = 'http://localhost:7071/api/run_agent';


export class DTAI {

    constructor() {
        this.dtai_user = DTAI_User.getInstance();
    }

    async getFlowOptions(body = null) {
        return new Promise(async (resolve, reject) => {

            await this.dtai_user.getAuth()
                .then(token => {

                            var options = {
                                method: body != null ? 'POST' : 'GET',  // or 'GET' if no data needs to be sent
                                headers: {
                                    'Content-Type': 'application/json; charset=UTF-8',
                                    'Authorization': `Bearer ${token["token"]}`,  // Include the API token in the Authorization header
                                    'x-user-id': this.dtai_user.getUser()
                                }
                            };
                            if (body != null) {
                                options.body = body;
                            }
                            return resolve(options);
                        })
                .catch(error => {
                    reject(error);
                });
        });
    }

    async loadFlow(flowName) {

        return new Promise(async (resolve, reject) => {

            var flowOptions = await this.getFlowOptions();
            // Make the request
            fetch(flowsFunctionUrl+"?"+new URLSearchParams({id:flowName}), flowOptions)
            .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    return resolve(response.json()); // or response.text() if the response is not in JSON format
            })
            .catch(error => {
                console.error('Failed to fetch:', error);
                reject(error);
            });
        });
    }
        
    async loadFlows() {
        return new Promise(async (resolve, reject) => {

            var flowOptions = await this.getFlowOptions();
            // Make the request
            fetch(flowsFunctionUrl, flowOptions)
            .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    return resolve(response.json()); // or response.text() if the response is not in JSON format
            })
            .catch(error => {
                console.error('Failed to fetch:', error);
                reject(error);
            });
        });
    }

    async saveFlow(flowData) {
        return new Promise(async (resolve, reject) => {

            var flowOptions = await this.getFlowOptions(flowData);
            // Make the request
            fetch(flowsFunctionUrl, flowOptions)
            .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    return resolve(response.json()); // or response.text() if the response is not in JSON format
            })
            .catch(error => {
                console.error('Failed to fetch:', error);
                reject(error);
            });
        });
    }

    async loadAgent(agentName) {
        return new Promise((resolve, reject) => {
            resolve({loadedData: "someData"})
        });
    }

    async saveAgent(agentData) {
        return new Promise((resolve, reject) => {
            resolve({savedData: "someData"})
        });
    }


}