from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.llms.llm import LLM

from prompts import TRAVEL_PLANNER_PROMPT

class TourInfo(BaseModel):
    airport_from: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the departure airport e.g. LHR, LAX etc.",
    )
    airport_to: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the destination airport e.g. LHR, LAX etc.",
    )
    departure_date: str = Field(
        ..., description="The departure date in the format YYYY-MM-DD"
    )
    return_date: str = Field(
        ..., description="The return date in the format YYYY-MM-DD"
    )
    destination: str = Field(
        ...,
        description="The destination where the user wants to visit.",
    )

class ExtractedInfo(BaseModel):
    reasoning: str = Field(
        ...,
        description="Your reasoning under 10 words behind the extracted information.",
    )
    tour_info: Optional[TourInfo] = Field(
        None, description="The extracted tour information."
    )


async def extract_tour_information(query: str, llm: LLM) -> ExtractedInfo:

    prompt = PromptTemplate(TRAVEL_PLANNER_PROMPT)
    response = llm.structured_predict(
        ExtractedInfo,
        prompt,
        query=query,
        date_today=datetime.now().strftime("%B %d, %Y"),
    )

    print(f"\n> Extracted user's request\n")
    return response
