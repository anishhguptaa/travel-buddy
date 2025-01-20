import requests
from typing import Any

from llama_index.core.llms.llm import LLM
from llama_index.core.workflow import (step, Context, Workflow, Event, StartEvent, StopEvent)
from markdown_pdf import MarkdownPdf, Section

from tools.flights import find_flights
from tools.hotels import find_hotels
from tools.places import find_places_to_visit

from agents.deligator import extract_tour_information
from agents.itinerary_writer import write_itinerary


class FlightsQueryData(Event):
    city_from: str
    city_to: str
    departure_date: str
    return_date: str


class DestinationData(Event):
    city: str


class HotelsQueryData(Event):
    city: str
    check_in_date: str
    check_out_date: str


class FlightsData(Event):
    flights_info: str


class PlacesToVisitData(Event):
    places_info: str


class HotelsData(Event):
    hotels_info: str

def md_to_html(markdown_content: str, html_file: str):
    headers = {"Content-Type": "text/plain", "charset": "utf-8"}
    html=requests.post("https://api.github.com/markdown/raw", headers=headers, data=markdown_content.encode("utf-8"))
    with open(html_file, "w", encoding='utf-8') as f:
        f.write(html.text)

class TravelPlannerWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm

    @step
    async def deligate_tasks(
        self, ctx: Context, ev: StartEvent
    ) -> FlightsQueryData | HotelsQueryData | DestinationData | StopEvent:
        query = ev.query
        await ctx.set("query", query)
        extracted_info = await extract_tour_information(query, self.llm)
        if not extracted_info.tour_info:
            return StopEvent(
                result=f"Failed to extract the correct information. Possible reason: {extracted_info.reasoning}.\nPlease try again with a different query."
            )
        await ctx.set("destination", extracted_info.tour_info.destination)
        ctx.send_event(
            FlightsQueryData(
                city_from=extracted_info.tour_info.airport_from,
                city_to=extracted_info.tour_info.airport_to,
                return_date=extracted_info.tour_info.return_date,
                departure_date=extracted_info.tour_info.departure_date,
            )
        )
        ctx.send_event(
            DestinationData(
                city=extracted_info.tour_info.destination,
            )
        )
        ctx.send_event(
            HotelsQueryData(
                city=extracted_info.tour_info.destination,
                check_in_date=extracted_info.tour_info.departure_date,
                check_out_date=extracted_info.tour_info.return_date,
            )
        )

    @step
    async def find_flights_step(self, ev: FlightsQueryData) -> FlightsData:
        flights_info = find_flights(
            ev.city_from, ev.city_to, ev.departure_date, ev.return_date
        )
        return FlightsData(flights_info=flights_info)

    @step
    async def find_hotels_step(self, ev: HotelsQueryData) -> HotelsData:
        hotels_info = find_hotels(ev.city, ev.check_in_date, ev.check_out_date)
        return HotelsData(hotels_info=hotels_info)

    @step
    async def find_sights_step(
        self, ev: DestinationData
    ) -> PlacesToVisitData:
        sights_info = find_places_to_visit(ev.city)
        return PlacesToVisitData(places_info=sights_info)

    @step
    async def print_itinerary(
        self,
        ctx: Context,
        ev: FlightsData | HotelsData | PlacesToVisitData,
    ) -> StopEvent:
        query = await ctx.get("query")
        destination = await ctx.get("destination")
        events = ctx.collect_events(
            ev, [FlightsData, HotelsData, PlacesToVisitData]
        )
        if events is None:
            return None

        flights_ev, hotels_ev, places_ev = events
        itinerary = await write_itinerary(
            query,
            destination,
            flights_info=flights_ev.flights_info,
            hotels_info=hotels_ev.hotels_info,
            sights_info=places_ev.places_info,
            llm=self.llm,
        )
        md_file = "itinerary.md"
        pdf_file = "itinerary.pdf"
        html_file = "itinerary.html"
        with open(md_file, "w") as f:
            f.write(itinerary)
        
        try:
            print(f"\n> Planned your tour to {destination}! Opening your itinerary PDF\n")
            pdf = MarkdownPdf()
            pdf.meta["title"] = 'Tour Itinerary'
            pdf.add_section(Section(itinerary, toc=False))
            pdf.save(pdf_file)
            return StopEvent(result=pdf_file)
        except Exception as e:
            print(f"\n> Couldn't convert markdown to pdf. Possible reason: {e}\n\n> Trying to open the itinerary in browser...\n")
            md_to_html(markdown_content=itinerary, html_file=html_file)
            return StopEvent(result=html_file)
