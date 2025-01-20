from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.llms.llm import LLM
from prompts import ITINERARY_WRITER_PROMPT

async def write_itinerary(
    query: str,
    destination: str,
    flights_info: str,
    hotels_info: str,
    sights_info: str,
    llm: LLM,
) -> str:
    print("\n> Planning your itinerary...\n")
    prompt = PromptTemplate(ITINERARY_WRITER_PROMPT)
    response = await llm.apredict(
        prompt,
        destination=destination,
        flights_info=flights_info,
        hotels_info=hotels_info,
        sights_info=sights_info,
        query=query,
    )

    return response
