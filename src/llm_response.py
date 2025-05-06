# from langchain.llms import Ollama
# from langchain.prompts import PromptTemplate
# import time
# from pathlib import Path
# import toml
# BASE_DIR = Path(__file__).resolve().parent.parent
# CONFIG_PATH = BASE_DIR / 'config' / 'config.toml'
# config = toml.load(CONFIG_PATH)

# class LLMInvoke:
#     def __init__(self):
#         self.model = config['LLMmodel']['model']
#         self.llm = Ollama(model=self.model)


#     def llm_response(self, query, context):
#         try:
#             prompt_template = PromptTemplate(
#                 input_variables=["query", "context"],
#                 template="""Answer strictly based on the context.\n\nContext: {context}\nQuestion: {query}\nAnswer:"""
#             )
#             prompt = prompt_template.format(query=query, context=context)

#             answer = self.llm(prompt)

#             result = {
#                 'answer': answer
#             }
#             return result

#         except Exception as e:
#             return {
#                 'answer': f"Error processing query: {str(e)}"
#             }


from pathlib import Path
import toml
import google.generativeai as genai
from langchain.prompts import PromptTemplate

# Load config
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.toml"
config = toml.load(CONFIG_PATH)

# Configure Gemini
api_key = config["geminiai"]["api_key"]
genai.configure(api_key=api_key)


class LLMInvoke:
    def __init__(self):
        self.model_name = config["geminiai"]["model"]
        self.model = genai.GenerativeModel(self.model_name)

    def llm_response(self, query, context):
        try:
            prompt_template = PromptTemplate(
                input_variables=["query", "context"],
                template="Briefly Answer strictly based on the context.\n\nContext: {context}\nQuestion: {query}\nAnswer:",
            )
            prompt = prompt_template.format(query=query, context=context)

            response = self.model.generate_content(prompt)

            return {"answer": response.text}

        except Exception as e:
            return {"answer": f"Error processing query: {str(e)}"}


# # Instantiate and test
# if __name__ == "__main__":
#     llm_handler = LLMInvoke()

#     query = "What are the benefits of exercise?"
#     context = (
#         "Exercise helps improve cardiovascular health, strengthen muscles, enhance flexibility, "
#         "and reduce stress. It can also support weight management and mental well-being."
#     )

#     response = llm_handler.llm_response(query=query, context=context)
#     print(response['answer'])


# import google.generativeai as genai

# genai.configure(api_key=api_key)

# models = genai.list_models()

# for model in models:
#     print(model.name)
