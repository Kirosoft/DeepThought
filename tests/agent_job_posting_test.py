import os
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
from core import process_request
import logging
import urllib3
from crewai_tools  import WebsiteSearchTool, SerperDevTool, FileReadTool

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]


### AI ###

searchTool = SerperDevTool()
websiteSearchTool = WebsiteSearchTool()

document = {"input": "hello","role":"research_analyst"}
result = process_request(json.dumps(document))
print(result['answer'])

if result["finish_reason"] == "stop" and result['answer_type'] == "user_input_needed":

    # company culture
    full_prompt = """Analyze the provided company website and the hiring manager's company's domain www.ukho.gov.uk. Focus on understanding the company's culture, values, and mission. Identify unique selling points and specific projects or achievements highlighted on the site. Compile a report summarizing these insights, specifically how they can be leveraged in a job posting to attract the right candidates."""
    document = {"input": full_prompt,"role":"research_analyst", "session_token": result["session_token"]}
    result = process_request(json.dumps(document))

    if result["finish_reason"] == "stop" and result['answer_type'] == "complete":
        print(result['answer'])

        # Hiring needs
        hiring_prompt="""Based on the hiring manager's needs: "Senior Software Engineer", identify the key skills, experiences, and qualities the ideal candidate should possess for the role. Consider the company's current projects, its competitive landscape, and industry trends. Prepare a list of recommended job requirements and qualifications that align with the company's needs and values. A list of recommended skills, experiences, and qualities for the ideal candidate, aligned with the company's culture, ongoing projects, and the specific role's requirements."""
        document = {"input": f"{hiring_prompt}","role":"research_analyst"}
        result = process_request(json.dumps(document))
        print(result['answer'])

        if result["finish_reason"] == "stop":
            document = {"input": f"{result['answer']}","role":"review_agent"}
            result = process_request(json.dumps(document))
            print(result)

else:
    print(f"ok we need to {result['answer']}")

