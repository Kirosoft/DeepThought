# TODO:
* Fix the timer auth token expiration in flows
* Fix the UI to work with settable properties
* support new nodes like: subflow, validate (compare ), log
* how will users manage flows?
* allow automated testing of flows using the ICL context style datasource
* Self learning roles
* fix the github actions deployment
* use LLM routing to lowest cost agent?

# WIP

* aim: allow the user to create a new role, associated contexts and tools from the terminal
* revisit tool calling so that agents (roles) can call other agents (which is a kind of tool). Tools can be 'azure functions' and specs define the parameters for tools.
* templates for tools? - should they inherit?
* LLM defined tools
* LLM defined UI for tools
* prefetch for agents based on available tools/roles/contexts
* 

Done:
<Strike>Agent roles can now be sourced from github - allows version control of role descriptions</strike><br/>
<Strike>Run agent returns conversing role when 'auto' mode is used.</strike><br/>
<Strike>Added 'valid_fields' to all objects stored to ensure fields not listed are not returned</strike><br/>
<Strike>Contexts support text lookup mode rather than just RAG</strike><br/>
<strike>Update all loaders to support multi url/file sources</strike><br/>
<strike>db layer now checks for 'valid_fields' attribute and removes any fields not listed</strike><br/>
<strike>auto agentic routing</strike><br/>
<strike>in-context learning added to flows</strike><br/>
<strike>in-context learning added to run_agent</strike><br/>
<strike>Add parsing support to the doc chunking</strike><br/>
<strike>support multiple txt doc sources for a single context</strike><br/>
<strike>support multiple pdf doc sources for a single context</strike><br/>
<strike>Context updates now have a versioning system so vectors can be updated and old values removed automatically</strike><br/>
<strike>Added durable timers to support mini context (RAG) updates</strike><br/>
<strike>Full agentic DAG(flows) now supported on the backend using durable orchestrations</strike><br/>
<Strike>Add support for Anthropic</strike><br/>
<Strike>Optional secrets now come from user account</strike><br/>
<Strike>RAG import from github repo</strike><br/>
<strike>role CRUD definitions to system, tenant or user</strike><br/>
<Strike>specs CRUD (system, tenant userid)</strike><br/>
<Strike>tools CRUD (system, tenant userid)</strike><br/>
<Strike>flow CRUD (system, tenant, user)</strike><br/>
<strike>* Multi-tenant support added to database and functions<br/></strike><br/>
<Strike>* Support multiple users<br/></strike><br/>
<strike>* Security - Added auth API to ensure secrets are not needed to be stored browser side<br></strike><br/>
<strike>* Security - Added rate limiting to the API<br></strike><br/>
<strike>* Security - Added request balance<br></strike><br/>
<strike>* Initial flow client created<br></strike><br/>
<strike>* Moved user options into DB<br></strike><br/>
<strike>* Implemented JWT token auth scheme<br></strike><br/>
<strike>* Security- Origin checks on requests<br></strike><br/>
<strike>* fix the ollama sdk to support function calling<br></strike><br/>
<Strike>* Local cosmodb init is slow ... <br></strike><br/>
<strike>* develop a job posting agent demo<br></strike><br/>
<Strike>* agent input expectation for multihop questions<br></strike><br/>
<Strike>* Improved LLM prompting i.e. system prompt, context, tools, examples <br></strike><br/>
<Strike>* Support JSON schema specification LLM outputs<br></strike><br/>
<strike>* LLM Model overrides from templates e.g. change the llm model based on the role<br></strike><br/>
<Strike>* rework <b>function calling</b> - now known as tools<br></strike><br/>
<Strike>* Add support for Grok<br/></strike><br/>
<strike>* Add support for local AI model - LLama3 - DONE<br></strike><br/>
<strike>* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE<br></strike><br/>
<strike>* Support <b>RAG</b> <br></strike><br/>
<strike>* Support <b>session memory</b> (Feature)</strike><br/>


