from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging
import urllib3
import types
from collections import namedtuple

# langchain loaders
from langchain.document_loaders import GithubFileLoader
from langchain_community.document_loaders import FireCrawlLoader
import urllib, PyPDF2
from io import BytesIO

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

loader_types = types.SimpleNamespace()
loader_types.GITHUB_FILE_LOADER = "github_file_loader"
loader_types.HTML_FILE_LOADER = "html_file_loader"
loader_types.PDF_FILE_LOADER = "pdf_file_loader"
loader_types.TEXT_FILE_LOADER = "text_file_loader"

class Document(object):
    metadata = {}
    page_content = ""
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata
    
class Loader:
    
    __loaders = None
    
    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.user_id = user_id
        self.tenant = tenant

        if Loader.__loaders is None:
            self.init_loaders()

        self.userdb = AgentDBBase(agent_config, agent_config.INDEX_USER, user_id, "system")
        self.user_keys = None

    def init_loaders(self):
        Loader.__loaders = {}
        self.register_loader(loader_types.GITHUB_FILE_LOADER, [
                {"name":"repo", "mandatory":True}, 
                {"name":"filter","mandatory":True, "default":[".md"]}, 
                {"name":"github_api_url","mandatory": True, "default":"https://api.github.com" },
                {"name":"github_key","mandatory": True, "default":"$GITHUB_KEY" }
            ])
        self.register_loader(loader_types.HTML_FILE_LOADER, [
            {"name":"url", "mandatory":True},
            {"name":"mode", "mandatory":True, "default":"crawl"}, # scape for single page mode, crawl for multi page
            {"name":"firecrawl_key","mandatory":True, "default":"$FIRECRAWL_API_KEY"}
        ])
        self.register_loader(loader_types.PDF_FILE_LOADER, [
            {"name":"url", "mandatory":True}
        ])
        self.register_loader(loader_types.TEXT_FILE_LOADER, [
            {"name":"url", "mandatory":True}
        ])
                                                                    
    def register_loader(self, loader_name, loader_args):
        Loader.__loaders[loader_name] = loader_args

    def get_schema(self, loader_name):
        return Loader.__loaders[loader_name] if loader_name in Loader.__loaders else None
    
    def resolve_variables(self, arg):

        # see if the arg needs to resolved to a user setting
        if arg[0] == "$":
            if self.user_keys is None:
                user_settings = self.userdb.get(self.user_id)
                self.user_keys = user_settings["keys"] if "keys" in user_settings else None
                
                if user_settings is None:
                    raise(f"Missing user settings ${self.user_id} ${self.tenant}")

            # resolve the value in user keys if available            
            return self.user_keys[arg[1:]] if arg[1:] in self.user_keys else arg
        return arg

    def get_args(self, loader_args,input_args):
        result_args = {}

        for arg in loader_args:
            # arg found as supplied in the input
            if arg["name"] in input_args:
                result_args[arg["name"]] = self.resolve_variables(input_args[arg["name"]])
            elif arg["mandatory"] and "default" in arg:
                result_args[arg["name"]] = self.resolve_variables(arg["default"])
            elif arg["mandatory"]:
                raise(f'Missing mandatory {arg["name"]}')
            else:
                # missing but not mandatory
                pass
        return result_args

    def run(self, loader_name, input_args):
        result = []

        match loader_name:
            case loader_types.GITHUB_FILE_LOADER:
                    
                    try: 
                        loader_args_spec = Loader.__loaders[loader_name]
                        loader_args  = self.get_args(loader_args_spec, input_args)

                        loader = GithubFileLoader(
                            repo=loader_args["repo"],
                            access_token=loader_args["github_key"],
                            github_api_url=loader_args["github_api_url"],
                            file_filter=lambda file_path: any(file_path.endswith(arg_path) for arg_path in loader_args["filter"])
                            )  
                        
                        result = loader.load()
                        return result
                    except Exception as e:
                        logging.error(f"error running loader: {e}")
                        return None
            case loader_types.HTML_FILE_LOADER:
                    
                    try: 
                        loader_args_spec = Loader.__loaders[loader_name]
                        loader_args  = self.get_args(loader_args_spec, input_args)
                        results = []

                        for url in loader_args["url"]:
                            loader = FireCrawlLoader(
                                api_key=loader_args["firecrawl_key"],
                                url=url,
                                mode=loader_args["mode"],
                            )
                            result = loader.load()
                            results.append(result)
                        return results
                    except Exception as e:
                        logging.error(f"error running loader: {e}")
                        return []

            case loader_types.PDF_FILE_LOADER:
                    try: 
                        loader_args_spec = Loader.__loaders[loader_name]
                        loader_args  = self.get_args(loader_args_spec, input_args)
                        result = []

                        for source in loader_args["url"]:
                            f = urllib.request.urlopen(source).read()
                            pdf_bytes = BytesIO(f)
                            pdf_reader = PyPDF2.PdfReader(pdf_bytes)

                            for page in pdf_reader.pages:
                                result.append(Document(page.extract_text(), {})) 

                        return result
                    except Exception as e:
                        logging.error(f"error running loader: {e}")
                        return []
            case loader_types.TEXT_FILE_LOADER:
                    try: 
                        loader_args_spec = Loader.__loaders[loader_name]
                        loader_args  = self.get_args(loader_args_spec, input_args)
                        result = []

                        for source in loader_args["url"]:
                            f = urllib.request.urlopen(source)
                            data = f.read()
                            f.close()
                            # TODO: read the bytes into the array
                            #result.append(Document(page.extract_text(), {}) for page in pdf_reader.pages)
                            page = namedtuple('literal', 'page_content metadata')(page_content=data.decode("utf-8"), metadata={"source":source})
                            result.append(page)

                        return result
                    except Exception as e:
                        logging.error(f"error running loader: {e}")
                        return []                    
        return None



