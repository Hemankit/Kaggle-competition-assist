from langchain.chat_models import ChatGroq
from langchain_core.messages import HumanMessage

# Replace this with your actual API key
api_key = "groq-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Instantiate the ChatGroq LLM
llm = ChatGroq(
    model="mistral-8x7b-32768",  # This is the exact model name
    api_key=api_key,
    temperature=0
)

# Send a test message
response = llm.invoke([
    HumanMessage(content="Say hello from Mistral!")
])

# Print the response
print(response.content)
