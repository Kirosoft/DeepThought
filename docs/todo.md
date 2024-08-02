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
* Contexts text lookup mode rather than just RAG

Done:
<strike>Update all loaders to support multi url/file sources</strike>
<strike>db layer now checks for 'valid_fields' attribute and removes any fields not listed</strike>
<strike>auto agentic routing</strike>
<strike>in-context learning added to flows</strike>
<strike>in-context learning added to run_agent</strike>
<strike>Add parsing support to the doc chunking</strike>
<strike>support multiple txt doc sources for a single context</strike>
<strike>support multiple pdf doc sources for a single context</strike>
<strike>Context updates now have a versioning system so vectors can be updated and old values removed automatically</strike>
<strike>Added durable timers to support mini context (RAG) updates</strike>
<strike>Full agentic DAG(flows) now supported on the backend using durable orchestrations</strike>
<Strike>Add support for Anthropic</strike>
<Strike>Optional secrets now come from user account</strike>
<Strike>RAG import from github repo</strike>
<strike>role CRUD definitions to system, tenant or user</strike>
<Strike>specs CRUD (system, tenant userid)</strike>
<Strike>tools CRUD (system, tenant userid)</strike>
<Strike>flow CRUD (system, tenant, user)</strike>
<strike>* Multi-tenant support added to database and functions<br/></strike>
<Strike>* Support multiple users<br/></strike>
<strike>* Security - Added auth API to ensure secrets are not needed to be stored browser side<br></strike>
<strike>* Security - Added rate limiting to the API<br></strike>
<strike>* Security - Added request balance<br></strike>
<strike>* Initial flow client created<br></strike>
<strike>* Moved user options into DB<br></strike>
<strike>* Implemented JWT token auth scheme<br></strike>
<strike>* Security- Origin checks on requests<br></strike>
<strike>* fix the ollama sdk to support function calling<br></strike>
<Strike>* Local cosmodb init is slow ... <br></strike>
<strike>* develop a job posting agent demo<br></strike>
<Strike>* agent input expectation for multihop questions<br></strike>
<Strike>* Improved LLM prompting i.e. system prompt, context, tools, examples <br></strike>
<Strike>* Support JSON schema specification LLM outputs<br></strike>
<strike>* LLM Model overrides from templates e.g. change the llm model based on the role<br></strike>
<Strike>* rework <b>function calling</b> - now known as tools<br></strike>
<Strike>* Add support for Grok<br/></strike>
<strike>* Add support for local AI model - LLama3 - DONE<br></strike>
<strike>* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE<br></strike>
<strike>* Support <b>RAG</b> <br></strike>
<strike>* Support <b>session memory</b> (Feature) <br></strike>


