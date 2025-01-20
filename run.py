import sys
import asyncio
import subprocess

# from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from workflow import TravelPlannerWorkflow

from dotenv import load_dotenv
load_dotenv()


async def main():
    # llm = OpenAI(model="gpt-4o-mini")
    llm = Gemini(model="models/gemini-1.5-flash")
    workflow = TravelPlannerWorkflow(llm=llm, verbose=False, timeout=240.0)
    query = sys.argv[1]
    result = await workflow.run(query=query)
    if ".pdf" in result or ".html" in result:
        subprocess.run(["open", result])


if __name__ == "__main__":
    asyncio.run(main())
