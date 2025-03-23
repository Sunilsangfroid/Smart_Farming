from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables")

def get_farming_response(question):
    model = ChatGoogleGenerativeAI(model='gemini-1.5-pro', api_key=google_api_key)
    prompt = PromptTemplate(
        input_variables=["query"],
        template="You are an agriculture expert. Answer the following question in detail: {query}"
    )
    # Wrap the prompt in a HumanMessage
    message = HumanMessage(content=prompt.format(query=question))
    # Call the model with a list of messages
    response = model([message])
    return response.content
