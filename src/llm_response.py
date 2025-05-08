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

