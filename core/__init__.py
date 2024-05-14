import logging

# Local 
#from core.agent.agent_llm import AgentLLM
from core.agent.agent_role import AgentRole
from core.agent.agent_memory import AgentMemory
from core.llm.llm_base import LLMBase
from core.agent.agent_config import AgentConfig


def process_request(body, user_id, tenant):
    agent_config = AgentConfig(body)

    if agent_config.is_valid():
        logging.info('core_llm_agent processed an event: %s',agent_config.input)
        agent_role = AgentRole(agent_config, user_id, tenant)
        agent_memory = AgentMemory(agent_config, user_id, tenant)

        llm = LLMBase(agent_config)

        # use the configured role to find the prompt and populate with the context and session history as required
        completed_prompt = agent_role.get_completed_prompt(agent_config.role)

        #llm_result = agent_llm.run_inference(completed_prompt, agent_config.input, agent_config.role, tools, routing)
        llm_result = llm.inference(completed_prompt)

        agent_memory.save_session_history(llm_result)

        return llm_result
    else:
        return None

