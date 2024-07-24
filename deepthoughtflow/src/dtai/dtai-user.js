

require("whatwg-fetch");

//const baseURL ="http://localhost:7071/api";
const baseURL ="https://deepthought-app.azurewebsites.net/api";

const authFunctionUrl = `${baseURL}/request_auth`;

export class DTAI_User {

    constructor(user, tenant) {

        if (DTAI_User.instance) {
            return DTAI_User.instance;
        }

        this.user = user ?? "ukho";
        this.password = tenant ?? "my_password"
        this.token = null;
    }

    static getInstance() {
        if (!DTAI_User.instance) {
            DTAI_User.instance = new DTAI_User();
        }
        return DTAI_User.instance;
    }

    getAuthRequestOptions() {
        return {
            method: 'GET',  // or 'GET' if no data needs to be sent
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'x-user-id': this.user,
                'x-password': this.password
                }
        };
    }

    getUser() {
        return this.user;
    }

    async getAuth() {
 
        return new Promise((resolve, reject) => {

            // TODO: this token will need to be refreshed every X minutes
            if (this.token != null) {
                return resolve(this.token);
            }
            else { 
                var authOptions = this.getAuthRequestOptions();

                // Make the auth request
                fetch(authFunctionUrl, authOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return resolve(response.json()); // or response.text() if the response is not in JSON format
                })
                .catch(error => {
                    console.error('Failed to fetch:', error);
                    return reject(error);
                });
            }
        });
    }
}