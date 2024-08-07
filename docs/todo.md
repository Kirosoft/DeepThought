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
* templates for tools? - should they inherit?
* LLM defined tools
* LLM defined UI for tools
* prefetch for agents based on available tools/roles/contexts
* 

* revisit tool calling so that agents (roles) can call other agents (which is a kind of tool). Tools can be 'azure functions' and specs define the parameters for tools.

Done:
* Now supports schema override like role overrides from contexts
* You can now define a <b>response_format</b> that is deterministic (openai models only) in each role - add 'schema' to role
* Agent roles can now be sourced from github - allows version control of role descriptions
* Run agent returns conversing role when 'auto' mode is used.
* Added 'valid_fields' to all objects stored to ensure fields not listed are not returned
* Contexts support text lookup mode rather than just RAG
* Update all loaders to support multi url/file sources
* db layer now checks for 'valid_fields' attribute and removes any fields not listed
* auto agentic routing
* in-context learning added to flows
* in-context learning added to run_agent
* Add parsing support to the doc chunking
* support multiple txt doc sources for a single context
* support multiple pdf doc sources for a single context
* Context updates now have a versioning system so vectors can be updated and old values removed automatically
* Added durable timers to support mini context (RAG) updates
* Full agentic DAG(flows) now supported on the backend using durable orchestrations
* Add support for Anthropic
* Optional secrets now comefrom user account
* RAG import from github repo
* role CRUD definitions to system, tenant or user
* specs CRUD (system, tenant userid)
* tools CRUD (system, tenant userid)
* flow CRUD (system, tenant, user)
* Multi-tenant support added to database and functions
* Support multiple users
* Security - Added auth API to ensure secrets are not needed to be stored browser side
* Security - Added rate limiting to the API
* Security - Added request balance
* Initial flow client created
* Moved user options into DB
* Implemented JWT token auth scheme
* Security- Origin checks on requests
* fix the ollama sdk to support function calling
* Local cosmodb init is slow ... 
* develop a job posting agent demo
* agent input expectation for multihop questions
* Improved LLM prompting i.e. system prompt, context, tools, examples 
* Support JSON schema specification LLM outputs
* LLM Model overrides from templates e.g. change the llm model based on the role
* rework <b>function calling</b> - now known as tools
* Add support for Grok
* Add support for local AI model - LLama3 - DONE
* Add support for a local and cloud vector/nosql database option - CosmosDB - DONE
* Support <b>RAG</b> 
* Support <b>session memory</b> (Feature)


