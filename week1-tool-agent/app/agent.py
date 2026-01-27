from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

llm = OpenAI(temperature=0)

tools = [
    Tool(name="Calculator", func=calculator, description="Useful for math operations")
]

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
