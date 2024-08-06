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
Agent roles can now be sourced from github - allows version control of role descriptions<br/>
Run agent returns conversing role when 'auto' mode is used.<br/>
Added 'valid_fields' to all objects stored to ensure fields not listed are not returned<br/>
Contexts support text lookup mode rather than just RAG<br/>
Update all loaders to support multi url/file sources<br/>
db layer now checks for 'valid_fields' attribute and removes any fields not listed<br/>
auto agentic routing<br/>
in-context learning added to flows<br/>
in-context learning added to run_agent<br/>
Add parsing support to the doc chunking<br/>
support multiple txt doc sources for a single context<br/>
support multiple pdf doc sources for a single context<br/>
Context updates now have a versioning system so vectors can be updated and old values removed automatically<br/>
Added durable timers to support mini context (RAG) updates<br/>
Full agentic DAG(flows) now supported on the backend using durable orchestrations<br/>
Add support for Anthropic<br/>
Optional secrets now come from user account<br/>
RAG import from github repo<br/>
role CRUD definitions to system, tenant or user<br/>
specs CRUD (system, tenant userid)<br/>
tools CRUD (system, tenant userid)<br/>
flow CRUD (system, tenant, user)<br/>
* Multi-tenant support added to database and functions<br/><br/>
* Support multiple users<br/><br/>
* Security - Added auth API to ensure secrets are not needed to be stored browser side<br><br/>
* Security - Added rate limiting to the API<br><br/>
* Security - Added request balance<br><br/>
* Initial flow client created<br><br/>
* Moved user options into DB<br><br/>
* Implemented JWT token auth scheme<br><br/>
* Security- Origin checks on requests<br><br/>
* fix the ollama sdk to support function calling<br><br/>
* Local cosmodb init is slow ... <br><br/>
* develop a job posting agent demo<br><br/>
* agent input expectation for multihop questions<br><br/>
* Improved LLM prompting i.e. system prompt, context, tools, examples <br><br/>
* Support JSON schema specification LLM outputs<br><br/>
* LLM Model overrides from templates e.g. change the llm model based on the role<br><br/>
* rework <b>function calling</b> - now known as tools<br><br/>
* Add support for Grok<br/><br/>
* Add support for local AI model - LLama3 - DONE<br><br/>
* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE<br><br/>
* Support <b>RAG</b> <br><br/>
* Support <b>session memory</b> (Feature)<br/>


