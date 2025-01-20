
# Travel Buddy

This project uses LLaMaIndex to orchestrate a sophisticated travel itinerary planner. It analyzes user preferences, suggests optimal flight and accommodation options, and curates personalized travel itineraries, all based on what you want to experience. It's like having a travel buddy who knows everything and may even suggest hidden gems ;)

## Stack used

- `LlamaIndex workflow` for orchestration.
- `SerpAPI` for finding flights, stays and tourist spots.
## How to use

- Clone the repo

```bash
git clone https://github.com/anishhguptaa/travel-buddy.git
cd travel-buddy
```

- Install dependencies

```bash
pip install -r requirements.txt
```

- Create `.env` file. Add `SERPAPI_KEY` and a LLM providor key:
_`OPENAI_API_KEY` to use OpenAI `gpt-4o-mini` model or `GOOGLE_API_KEY` for the Gemini `gemini-1.5-flash` model_

```bash
cp .env.example .env
```

- Run the workflow with the topic to research. Example:

```bash
python run.py "Plan a 10 days trip from Delhi to Dubai for next next month"
```

## Future scope

- Adding a to and fro mechanism to further optimise the travel itinerary.
