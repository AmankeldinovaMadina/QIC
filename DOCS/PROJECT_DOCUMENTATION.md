# QIC Travel Planner — Project Documentation

## 1. Project Overview

QIC Travel Planner is an AI-enhanced travel planning platform built with FastAPI (Python) and a modern frontend (Vite/React). It provides AI-assisted trip planning, search and ranking for hotels, flights, entertainment, and trip management (itineraries, ICS export). The platform uses structured outputs from OpenAI for complex responses (trip plans, rankings) and integrates third-party APIs (Google Maps, SerpApi) to fetch venue/hotel information. It also stores trip and ranking artifacts in a database for persistence.

### Purpose
- Help users plan better trips faster via a conversational AI companion.
- Deliver high-value, actionable recommendations (hotels, entertainment) with direct links and CTAs for purchases (insurance, bookings).
- Increase QIC ecosystem engagement, DAU, and monetizable conversions by integrating AI-driven UX and targeted promotional flows.

### Core Capabilities
- AI-generated trip planning (structured TripPlan objects).
- AI and heuristic ranking for hotels and entertainment with link preservation.
- Persisted culture guides and selected items by `trip_id`.
- Trip ICS export and shareable trip summary to encourage social sharing and referrals.
- Voice and chat driven AI companion to guide users through planning and booking flows.

### Contract (inputs/outputs, success criteria)
- Inputs: Trip request (dates, destinations, preferences), lists of venues/hotels, user profile if authenticated.
- Outputs: Structured TripPlan, ranked lists (with links), CultureGuide saved by trip_id, trip summary text/ICS.
- Success criteria: Accurate structured TripPlan validated by Pydantic, ranked items include actionable links, AI companion supports helpful chat/voice flows that guide users to buy services (insurance, bookings).

### Edge cases to watch
- Missing/partial input data (e.g., no dates, missing timezone).
- Network failures to external APIs (SerpApi, Google Maps, RapidAPI).
- OpenAI rate limits or model errors (fallback to heuristic ranking).
- Auth/permissions for endpoints (entertainment endpoints expect authenticated users).
- User privacy — consent for marketing/promotions.

---

## Feature Reference — how each feature works and technical implementation

This section breaks down each major feature, describes how it behaves from a user perspective, and lists the concrete technical implementation details (endpoints, modules, schemas, DB models, and tests). Use these notes when implementing changes or building integrations.

### 1) Trip Planner (AI-generated TripPlan)

How it works
- User submits trip parameters (dates, destinations, preferences) via the UI or API.
- Backend calls the OpenAI Responses API with a system prompt and the request payload; the model returns a structured TripPlan which is validated and normalized.
- The assistant may follow up with clarifying prompts; the final TripPlan is stored or returned to the client.

Technical implementation
- Endpoint: POST `/ai/plan` (top-level `app.py`) — handler `ai_plan` accepts `PlanRequest` and returns `PlanResponse`.
- Core code: `generate_trip_plan_structured(req: PlanRequest)` in `app.py` uses `client.responses.parse(..., text_format=TripPlan)` to parse directly to the Pydantic model.
- Schema: `TripPlan`, `TripDay`, `TripEvent` defined in `app.py` (Pydantic). Validation/normalization occurs in `_normalize_trip_plan`.
- Error handling: If model returns incomplete/invalid output, the endpoint raises HTTP 502 with details.
- Tests: add unit tests that mock `client.responses.parse` to return valid/invalid outputs; assert validation and normalization behavior.

### 2) AI Companion (Chat + Voice)

How it works
- Embedded on every page as a conversational widget. Users can type or speak commands.
- Assistant uses current trip context (if any) and the model to interpret commands and produce actions (edits, rankings, CTAs).

Technical implementation
- Frontend: chat widget component (React) that opens a conversation and streams messages. Voice uses Web Speech API for STT/TTS or a cloud provider.
- Backend session management: a chat session record (session_id) is passed to the OpenAI prompt to preserve context; store conversation metadata in DB if needed.
- Server connectors: existing OpenAI client (`OpenAI(api_key=...)` in `app.py`) can be reused; consider creating a dedicated chat connector under `app/ai/` or `backend/app/ai` to centralize prompt templates and rate-limit logic.
- Security: require explicit opt-in for saving voice transcripts; provide endpoints to purge conversation history.

### 3) Hotel ranking (AI + heuristic fallback)

How it works
- Frontend supplies a list of hotel search results (from SerpApi or other provider) and user preferences.
- Backend calls the AI ranker to order hotels by suitability and returns a ranked list containing hotel metadata and booking links.

Technical implementation
- Endpoint: POST `/api/v1/hotels/rank` (router in `app/hotels/router.py`).
- Ranker: `app/hotels/ai_ranker.py` containing `OpenAIHotelRanker` and heuristic fallback. It builds `hotels_by_id`, calls OpenAI with a structured response schema, and if that fails, runs `_heuristic_ranking`.
- Schemas: `app/hotels/schemas.py` includes `HotelForRanking`, `HotelRankItem`, `HotelSelectionRequest`, and `SelectedHotelInfo`. `link` field was added to these models and persisted.
- DB: selected hotel link is persisted in `trips` table via `selected_hotel_link` column (see `app/db/models.py` and migration `migrate_hotel_link.py`).
- Tests: `test_hotel_ranking_link.py` and `test_verify_link_field.py` validate that `link` is included and persisted.

### 4) Entertainment ranking (AI + heuristic fallback)

How it works
- Similar to hotels: a list of Google Maps venues is passed with user preferences; ranker returns ordered venues and preserves `link` (Maps URL).
- This endpoint may require authentication depending on router settings.

Technical implementation
- Endpoint: POST `/api/v1/entertainment/rank` (router in `app/entertainment/router.py`). Note: this router often uses `get_current_user` dependency for protected routes.
- Ranker: `app/entertainment/ai_ranker.py` contains `OpenAIEntertainmentRanker` and fallback `_heuristic_ranking`. The ranker maps `place_id` to original venue objects to copy `link` into the result items.
- Schemas: `app/entertainment/schemas.py` contains `GoogleMapsVenue`, `EntertainmentRankItem`, and `EntertainmentRankRequest` — a `link: Optional[str]` field was added to venue and item schemas.
- Tests: `test_entertainment_ranker_direct.py` exercises the ranker without API auth and confirms `link` preservation. Endpoint-level tests need auth fixtures.

### 5) Culture Guide (generate & persist per trip)

How it works
- User or assistant requests a culture guide for a trip; backend generates a city/culture-specific guide via OpenAI and stores it by `trip_id` for later retrieval.

Technical implementation
- Endpoints: POST `/api/v1/culture/guide` (generate & persist), GET `/api/v1/culture/guide/{trip_id}` (retrieve) implemented in `app/culture/router.py`.
- DB model: `CultureGuide` added to `app/db/models.py` with fields `trip_id`, `destination`, `summary`, `tips_json`, `created_at`.
- Migration: `migrate_culture_guide.py` creates the `culture_guides` table.
- Caching: on POST, if a guide already exists for the trip, return cached guide to avoid repeated model calls.

### 6) Flight Link (Skyscanner redirect)

How it works
- Frontend sends flight search parameters; backend builds a Skyscanner URL that the frontend can redirect the user to.

Technical implementation
- Endpoint: POST `/flight/link` in `app.py`, handler `flight_link(filters: FlightTicketsModel)`.
- URL builder: `url_builder.TripFilters` maps `FlightTicketsModel` fields to Skyscanner URL structure; `url_builder.build_url(tf)` constructs the link.
- Schema: `FlightTicketsModel` and `FlightLinkResponse` in `app.py`.

### 7) Trip summary & ICS export

How it works
- AI or user triggers a trip summary creation and optionally an ICS file for calendar import.
- Summary is formatted for sharing and may include CTAs (bookings, insurance) in the UI.

Technical implementation
- Endpoints: POST `/ai/plan/ics` and `/ai/plan/ics-file` in `app.py`. They reuse `generate_trip_plan_structured` and `plan_to_ics`.
- Formatter: `plan_to_ics` in `app.py` converts TripPlan -> RFC-5545-ish ICS text.
- Sharing: create a short share text using the model; optionally produce HTML snippet with links.

### 8) Visa services (RapidAPI)

How it works
- User queries visa requirements or requests a passport-rank calculation; backend forwards to RapidAPI service and returns the results.

Technical implementation
- Endpoints: GET `/visa/check` and POST `/visa/rank/custom` in `app.py`.
- Network: `httpx.AsyncClient` used to call RapidAPI endpoints; headers are `VISA_HEADERS`.
- Errors: wrap network errors and return appropriate HTTP 502 or 500 codes.

### 9) DB models & migrations

How it works
- Data that needs persistence (trips, culture guides, selected links, users) is stored in the DB. Migrations are provided as scripts.

Technical implementation
- Models: `app/db/models.py` holds SQLAlchemy ORM models (async). Key additions include `CultureGuide` and `selected_hotel_link` on trips.
- Migrations: ad-hoc scripts such as `migrate_hotel_link.py` and `migrate_culture_guide.py` are used to update sqlite schema.
- Recommendation: adopt a formal migration tool (Alembic with async support) for production workflows.

### 10) Authentication & security

How it works
- Some endpoints require authentication (entertainment routes). The system keeps user profiles for persisted trips and consent flags for marketing.

Technical implementation
- Dependency: `get_current_user` is used in routers like `app/entertainment/router.py` to enforce authentication.
- Storage: user records and tokens live in `app/db/models.py`; sensitive data should be encrypted and consent flags tracked.
- Tests: use fixtures to create test users and JWT tokens or bypass dependencies in unit tests.

### 11) Testing strategy & CI

How it works
- Unit tests for logic-heavy modules (rankers, trip normalization) and integration tests for endpoints. Simulate OpenAI & external API responses where possible.

Technical implementation
- Tests in repo: multiple test files (`test_entertainment_ranker_direct.py`, `test_hotel_ranking_link.py`, etc.).
- Mocking: mock `client.responses.parse`, `httpx.AsyncClient` and external APIs to validate behavior without calling external services.
- CI: integrate `pytest` into CI and fail builds when critical coverage thresholds drop.

---
## 2. AI Companion — Chat and Voice Assistant

### Overview
- Every page (or major flow) in the product will display an AI Companion UI element. Users can interact via:
  - Chat (text): Type questions and commands (e.g., "Add a sushi restaurant to day 2").
  - Voice: Short voice commands (speech-to-text) and TTS responses (voice assistant).
- The AI Companion will operate in two modes:
  - Navigation & guidance mode: Help users navigate the product, explain features, and call out CTAs.
  - Task mode: Modify trip plans, re-run rankings, suggest bookings, prepare trip summaries, and step-by-step planning.

### Capabilities
- Natural language planning: Transform user intents into concrete TripPlan edits (add/remove events, change pacing).
- Ranking & filtering: Ask the assistant "Show me top halal-friendly places" and it will filter/rerank accordingly.
- Booking CTAs: When recommending a hotel or transport, the AI will present the booking link and optional insurance CTA.
- Trip summary generation: Create share-ready summaries and social snippets (short text + suggested hashtags).
- Guided onboarding: Teach users about QIC services and how to use features.

### Interaction patterns
- Chat examples:
  - User: "Plan a 5-day Tokyo trip for two, include one luxury hotel and street food spots."  
    AI: Returns a TripPlan preview, asks clarifying questions, then persists the plan.
  - User: "Find me museums near my hotel and book tickets if possible."  
    AI: Returns ranked museum list, includes links, suggests ticket purchase or partner buy flow.
- Voice examples:
  - User (voice): "Add Tsukiji Market to day 2 after breakfast."  
    Assistant: "Done — I've added Tsukiji Market on day 2 at 10:30. Want me to add directions?"

### AI Companion architecture
- Frontend components: Chat UI + microphone button + message history panel + small contextual suggestions.
- Backend:
  - Chat session management (session_id, user_id, conversation state).
  - Connector to OpenAI responses API for structured outputs and chat messages.
  - Voice: speech-to-text (e.g., Web Speech API or a cloud STT provider) and text-to-speech for responses.

### Quality-of-life features
- Suggested quick actions: "Add transfer", "Buy travel insurance", "Share trip".
- Context-aware prompts: AI prompts include trip context (TripPlan, selected hotels, preferences) for precise suggestions.
- Local caching: Store conversation context to avoid repeated full-model calls and minimize cost.

### Privacy & user control
- All marketing/promotional CTAs (insurance prompts, partner links) are opt-in by default; allow users to disable promotions in settings.
- Transcripts and voice data retention are configurable; provide an option to delete conversation history.

---

## 3. AI Concept & Logic

### Design principles
- Use structured outputs for deterministic data (TripPlan Pydantic model).
- Use AI for creative or ranking tasks, but implement deterministic fallbacks (heuristic ranking).
- Persist outputs that matter (culture guides, selected hotel link) keyed by `trip_id` for reusability and auditability.

### Primary AI usage patterns
- Structured TripPlan generation: Use a system prompt and OpenAI structured response parsing to produce `TripPlan` objects which are validated and normalized.
- Ranking: Use OpenAI to score or order items by preference (sent as venues/hotels list + user preferences). If OpenAI fails or is rate-limited, a heuristic ranking produces deterministic results.
- Summaries: Use the model to create concise trip summaries for sharing.
- QA & guidance: Conversational assistant uses model for interpretation and action mapping.

### Implementation notes (from codebase)
- OpenAI client uses `responses.parse` with a `text_format` to get structured `TripPlan` directly.
- When parsing OpenAI responses for rankings, the code attempts to map back item IDs (`place_id` or `serp_id`) to original venues/hotels to preserve link fields.
- On failure of OpenAI ranking (parsing errors or type errors), the code falls back to heuristic ranking, ensuring uninterrupted UX.

### Cost & rate limits
- Use caching (persisted culture guides and previously ranked results) to avoid repeated model calls.
- Consider batching and context truncation:
  - Send only necessary fields to the model (title, rating, price, description).
  - Keep user preferences concise but explicit.
- Monitor model usage and provide fallback messaging to users when AI is degraded.

---

## 4. User Flows & UX (with AI Companion)

### High-level flows
1. New user onboarding
   - AI companion greets, asks for travel intent, and suggests a sample trip.
   - Users are guided to create a trip (dates, destinations, preferences).
2. Trip planning
   - User enters trip details → backend calls OpenAI to generate a TripPlan → AI companion explains plan & offers edits.
3. Search & ranking
   - Hotels/entertainment searches return ranked lists with links. AI assistant can rerank/filter using natural language.
4. Add-ons / Monetization CTAs
   - At relevant points (transport choice, booking, before final confirmation), the assistant suggests insurance or other partner products (targeted CTA).
   - Example: If user chooses a rental car as transport, prompt: "Would you like to add car insurance for your rental?"
5. Trip summary & sharing
   - AI generates a shareable trip summary and suggested social copy.
   - CTA: "Share this summary" to social or send to friends via email/messages.
6. Persisted culture guide
   - Generate culture guide per trip and store it keyed by `trip_id`; user can fetch it later via GET or ask the AI to summarize again.

### Detailed UX examples
- Booking flow with CTA:
  - User selects a hotel from ranked results.
  - The details panel shows hotel link + "Buy travel insurance" button. Clicking opens a modal with partner options and pricing.
- Voice navigation:
  - Mic → "Show me the best sushi spots near my hotel" → assistant reads top-3 and offers to add one to itinerary.
- Onboarding to QIC services:
  - Assistant highlights lesser-known services (visa checks, passport rank) with in-chat links.

### Accessibility & usability
- Keyboard-first chat, screen-reader friendly message labels.
- Voice commands support simple, unambiguous tasks; complex edits fallback to chat UI.

---

## 5. Monetization & Business Benefits for QIC

### How AI increases revenue and engagement
- Personalized prompts and contextual CTAs raise conversion rates:
  - Insurance CTAs: Recommend travel insurance at checkout and suggest specific policies when user adds flights or chooses car transport. Example: If transport type == "car", present car insurance options.
  - Cross-sell: Trip summary shows recommended add-ons (airport transfers, guided tours) with partner offers.
- Increased Daily Active Users (DAU) and session length:
  - AI companion invites users to explore, experiment with plans, and return to refine trips.
- Viral acquisition via shareable trip summaries:
  - Users share AI-crafted itineraries on social media, driving organic growth and referrals.
- Better user retention:
  - An assistant that teaches users how to use the platform reduces churn and increases product stickiness.

### Concrete calls-to-action (CTA) examples
- Insurance CTA: "Before you finalize, would you like 10% off travel insurance for this trip?" (show partner offer)
- Car-specific CTA: "You selected car as transport — add car insurance for only $X/day."
- Upgrade CTA: "Upgrade to premium itinerary services and get concierge booking for hotels/experiences."

### KPIs to measure success
- Conversion rate on CTAs (insurance, booking clicks)
- DAU and average session duration
- Average revenue per user (ARPU)
- Share-to-acquisition ratio (shares → new signups)
- Model call rate and fallback frequency (OpenAI vs heuristic)

### Revenue projection rationale
- If a modest conversion lift (e.g., 1-3%) is achieved through targeted AI CTAs and guided upsells, this scales linearly with traffic and bookings.
- Car-insurance CTA is especially high-intent: users selecting car transport are more likely to add insurance.

---

## 6. Developer Guide — Setup & Running Locally

### Prerequisites
- Python 3.11+ (the repo used Python 3.13 in some terminals; 3.11-3.13 should be fine).
- pip and virtualenv or preferred environment manager (venv, conda).
- Environment variables:
  - `OPENAI_API_KEY` — required
  - `RAPIDAPI_KEY` — (for visa API) optional but recommended
  - `GOOGLE_MAPS_API_KEY` — for Google Maps / Places
  - `SERPAPI_KEY` — for hotel search (if used)
  - `DATABASE_URL` — e.g., `sqlite+aiosqlite:///./qic.db` or other DB URI
- Optional: credentials for partner insurance APIs if integrating live offers.

### Install & run
1. Create virtualenv and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (macOS zsh example):
```bash
export OPENAI_API_KEY="sk-..."
export RAPIDAPI_KEY="..."
export GOOGLE_MAPS_API_KEY="..."
export DATABASE_URL="sqlite+aiosqlite:///./qic.db"
```

3. Run migrations (if present) or the migration scripts included (e.g., `migrate_hotel_link.py`):
```bash
python migrate_hotel_link.py
python migrate_culture_guide.py
```

4. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8001
# or, if running the top-level app.py:
python app.py
```

5. Run tests:
```bash
pytest -q
# Or run single test:
python test_entertainment_ranker_direct.py
```

### Developer notes
- The app uses async SQLAlchemy sessions. Ensure your DB driver supports async (`aiosqlite` for sqlite).
- For local OpenAI testing, consider using a sandbox key or mock responses to avoid cost.
- Some entertainment endpoints require authentication (`get_current_user` dependency). Use test fixtures that create users and tokens when running endpoint-level tests.

### Extending AI rankers
- To add new fields to be preserved from input through ranking:
  1. Add the field to input schema (e.g., `GoogleMapsVenue`).
  2. Update the ranker’s `venues_by_id` mapping to include the field when building output items.
  3. Update the Pydantic output model (`RankItem`) to include the field.
  4. Add tests that create sample input with that field and verify it appears in the resulting `RankItem`.

### Important files to check
- `app/main.py` — application entrypoint and router wiring.
- `app/db/models.py` — SQLAlchemy models including `CultureGuide` and `selected_hotel_link`.
- `app/entertainment/ai_ranker.py` & `app/hotels/ai_ranker.py` — ranking logic and link passthrough.
- `app/entertainment/schemas.py` & `app/hotels/schemas.py` — Pydantic schemas.

---

## 7. API Reference (selected endpoints)
- GET `/health` — health check.
- POST `/ai/plan` — generate structured TripPlan. Request: `PlanRequest`, Response: `PlanResponse`.
- POST `/flight/link` — generate Skyscanner redirect link. Request: `FlightTicketsModel`.
- POST `/api/v1/culture/guide` — generate and persist culture guide for a trip (`trip_id`).
- GET `/api/v1/culture/guide/{trip_id}` — retrieve saved culture guide.
- POST `/api/v1/hotels/rank` — rank hotels. Response items include `link` fields for hotels.
- POST `/api/v1/entertainment/rank` — rank entertainment venues (authentication required in router). Response includes `link` fields for venues.

Note: Some endpoints have authentication requirements (entertainment routes). Ensure tests supply tokens or use unit tests bypassing dependency injection.

---

## 8. Trip Summaries & Social Sharing

### Trip summary features
- Short summary text with highlights and top recommendations.
- Formatted ICS export for calendar import.
- Shareable HTML/text + suggested social captions.

### Engagement benefits
- Shareable content increases brand awareness and can drive sign-ups.
- Summary includes CTAs (book now, buy insurance) that appear in shared views (where appropriate) to drive conversions.

### Sample share snippet (auto-generated)
- “My 5-day Tokyo plan: Highlights — Tokyo Skytree, Senso-ji, Tsukiji Market. Got it from QIC Travel Planner — plan yours: [link].”

---

## 9. Security, Privacy & Compliance

### Data handling
- Store minimal PII. Associate trip artifacts with user ID (if authenticated).
- Encrypt sensitive data at rest and in transit (HTTPS).
- Provide users with data controls: export, delete, opt-out of marketing.
- Log access to AI assistant transcripts and interactions; purge voice transcripts unless opted-in.

### Marketing & promotions
- Consent-first: explicit opt-in for targeted marketing (insurance offers).
- Give users ability to dismiss or disable promotional prompts in settings.

### OpenAI Data Policy
- Comply with OpenAI policy: do not send PII without consent; mask sensitive personal data from prompts where not necessary.

### Legal & partner offers
- When presenting partner insurance, include partner name, price, terms, and privacy notice.
- For certain countries, insurance or financial product promotions may require disclosures or licensing—consult legal team before live deployment.

---

## 10. Monitoring, QA & Roadmap

### Monitoring
- Track model call usage and fallback rate (OpenAI success vs heuristic).
- Monitor CTA conversion rates and DAU.
- Logging for AI companion interactions (sanitized).

### Tests
- Unit tests for rankers (happy path and fallback).
- Integration tests for endpoints (authenticated and unauthenticated flows).
- End-to-end test for trip creation → ranking → booking CTA.

### Roadmap (3–6 months)
- 1. Robust voice assistant (bi-directional voice, seamless STT/TTS).
- 2. Personalization engine: learn user preferences to improve ranking.
- 3. Partner integrations for in-app booking and insurance purchase APIs.
- 4. AB testing for different CTA placements and messaging.
- 5. Mobile SDKs for embedding AI companion across QIC ecosystem (deep links to bookings).

---

## 11. Example Prompts & Assistant Dialogs

### Action mapping examples
- "Add 2 nights at a 4-star hotel near Tokyo Skytree" → Create hotel selection subflow and present top hotels with links + optional insurance CTA.
- "Make day 3 more relaxed" → Assistant modifies timestamps and rebalances events.

### Sample chat flow
- User: "I want fewer museum visits, more food experiences."
- AI: "I can reorder the plan. Shall I replace one museum with a food market on day 2?"
- User: "Yes, and push the museum to day 4."
- AI: Performs the update and presents the new TripPlan.

---

## 12. Adoption Playbook for QIC (How this helps QIC ecosystem)
- Drive DAU: AI Companion keeps users engaged, increases visits per user.
- Increase ARPU: Contextual CTAs (insurance, upgrades) at high intent moments increase conversion.
- Reduce friction: Conversational onboarding helps users understand QIC’s full service list.
- Improve referrals: Shareable itineraries lead to organic growth.

### Go-to-market ideas
- Offer “AI-curated itinerary” free for 1st trip; promote insurance/concierge upsell at checkout.
- Partner bundles: Integrate partner offers (insurance, guided tours) and highlight them via assistant suggestions.

---

## 13. Next Steps & Recommendations

### Immediate technical next steps
- Add automated endpoint tests that authenticate and test entertainment ranking CTAs.
- Implement a minimal voice assistant POC using browser STT/TTS; connect to existing chat flow.
- Add opt-in setting for marketing/promotions and record consent flags in user profile.

### Business recommendations
- Run AB tests on CTA placement (ranked results vs. trip summary modal).
- Build partner program for insurance and travel services to provide discounted CTAs.

---

## 14. Appendix — Useful Commands / Quick Reference

Run server (dev):
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
# or run app.py directly
python app.py
```

Run the direct ranker test (no auth):
```bash
python test_entertainment_ranker_direct.py
```

Run full test suite:
```bash
pytest -q
```

Migrate DB (example scripts):
```bash
python migrate_hotel_link.py
python migrate_culture_guide.py
```

Environment variables (example .env):
```
OPENAI_API_KEY=sk-...
RAPIDAPI_KEY=...
GOOGLE_MAPS_API_KEY=...
SERPAPI_KEY=...
DATABASE_URL=sqlite+aiosqlite:///./qic.db
```

---

## Completion summary
- I created a comprehensive project documentation that: describes the AI companion (chat + voice), details AI logic and fallbacks, maps user flows, explains monetization via CTAs (insurance/car insurance), and includes developer/run instructions plus monitoring and roadmap. The documentation also emphasizes privacy and legal considerations and provides sample prompts & dialogs.

If you'd like this split into multiple files (Overview, AI Companion, Developer Guide, Monetization, Privacy), I can create a `DOCS/` landing README and separate pages.
