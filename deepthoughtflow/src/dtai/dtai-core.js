

import {DTAI_User} from "./dtai-user.js";
require("whatwg-fetch");


//const baseURL ="http://localhost:7071/api";
const baseURL ="https://deepthought-app.azurewebsites.net/api";

const flowsFunctionUrl = `${baseURL}/flows_crud`;
const rolesFunctionUrl = `${baseURL}/roles_crud`;
const runAgentFunctionUrl = `${baseURL}/run_agent`;


export class DTAI {

    constructor() {
        this.dtai_user = DTAI_User.getInstance();
    }

    async getHeaderOptions(body = null) {
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

            var flowOptions = await this.getHeaderOptions();
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

            var flowOptions = await this.getHeaderOptions();
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

            var flowOptions = await this.getHeaderOptions(flowData);
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

    async runAgent(payload) {
        return new Promise(async (resolve, reject) => {

            var roleOptions = await this.getHeaderOptions(payload);
            // Make the request
            fetch(runAgentFunctionUrl, roleOptions)
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


    async saveRole(roleData) {
        return new Promise(async (resolve, reject) => {

            var roleOptions = await this.getHeaderOptions(roleData);
            // Make the request
            fetch(rolesFunctionUrl, roleOptions)
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
    
    async loadRoles() {
        return new Promise(async (resolve, reject) => {

            var roleOptions = await this.getHeaderOptions();
            // Make the request
            fetch(rolesFunctionUrl, roleOptions)
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


}