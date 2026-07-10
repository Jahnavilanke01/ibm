import os
import textwrap
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ── IBM watsonx.ai Configuration ──────────────────────────────────────────────
WATSONX_API_KEY  = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL      = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT  = os.getenv("WATSONX_PROJECT_ID", "")
GRANITE_MODEL_ID = "ibm/granite-13b-instruct-v2"

# Demo mode is active when real credentials are not supplied
DEMO_MODE = not (WATSONX_API_KEY and WATSONX_PROJECT
                 and WATSONX_API_KEY != "your_ibm_cloud_api_key_here"
                 and WATSONX_PROJECT != "your_watsonx_project_id_here")


def get_watsonx_model():
    """Initialise and return a Granite ModelInference client."""
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

    credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_API_KEY)
    params = {
        GenParams.MAX_NEW_TOKENS:      1024,
        GenParams.MIN_NEW_TOKENS:      100,
        GenParams.TEMPERATURE:         0.7,
        GenParams.TOP_P:               0.9,
        GenParams.TOP_K:               50,
        GenParams.REPETITION_PENALTY:  1.1,
    }
    return ModelInference(
        model_id=GRANITE_MODEL_ID,
        credentials=credentials,
        project_id=WATSONX_PROJECT,
        params=params,
    )


def build_itinerary_prompt(data: dict) -> str:
    """Construct a structured prompt from user travel preferences."""
    destination  = data.get("destination", "")
    duration     = data.get("duration", "7")
    travel_style = data.get("travel_style", "balanced")
    budget       = data.get("budget", "moderate")
    interests    = ", ".join(data.get("interests", [])) or "general sightseeing"
    travelers    = data.get("travelers", "solo")
    start_date   = data.get("start_date", "flexible")
    special_reqs = data.get("special_requirements", "none")

    return textwrap.dedent(f"""
        You are an expert travel planner. Create a detailed, personalized day-by-day travel itinerary.

        Destination: {destination}
        Duration: {duration} days
        Travel Style: {travel_style}
        Budget Level: {budget}
        Interests: {interests}
        Travelers: {travelers}
        Start Date: {start_date}
        Special Requirements: {special_reqs}

        Please provide:
        1. A brief destination overview
        2. Day-by-day schedule (morning / afternoon / evening)
        3. Recommended restaurants and local cuisine
        4. Transportation tips
        5. Accommodation suggestions matching the budget
        6. Packing tips
        7. Important local customs or travel tips

        Format clearly with each day as a section. Include place names, estimated costs, and practical advice.

        ITINERARY:
    """).strip()


def demo_itinerary(data: dict) -> str:
    """Return a rich hard-coded sample itinerary used when credentials are absent."""
    destination  = data.get("destination", "your destination")
    duration     = data.get("duration", "7")
    travelers    = data.get("travelers", "solo traveler")
    budget       = data.get("budget", "moderate")
    travel_style = data.get("travel_style", "balanced")
    interests    = ", ".join(data.get("interests", [])) or "general sightseeing"

    return textwrap.dedent(f"""
        ╔══════════════════════════════════════════════════════════╗
        ║   DEMO MODE — Connect IBM watsonx.ai for live Granite   ║
        ║   output.  Add credentials to travel_planner/.env       ║
        ╚══════════════════════════════════════════════════════════╝

        **{duration}-Day Itinerary for {destination}**
        Traveler: {travelers} | Style: {travel_style} | Budget: {budget}
        Interests: {interests}

        ─────────────────────────────────────────────────────────────
        DESTINATION OVERVIEW
        ─────────────────────────────────────────────────────────────
        {destination} is a captivating destination blending rich history,
        vibrant culture, and stunning landscapes. This personalised itinerary
        is crafted to match your travel style and interests, ensuring an
        unforgettable journey from the very first day.

        ─────────────────────────────────────────────────────────────
        Day 1 — Arrival & First Impressions
        ─────────────────────────────────────────────────────────────
        Morning:   Arrive and check in to a centrally located hotel (~$80–120/night
                   for {budget} budget). Freshen up and grab a local breakfast.
        Afternoon: Take a gentle orientation walk around the city centre.
                   Visit the main plaza or waterfront promenade.
        Evening:   Welcome dinner at a highly-rated local restaurant.
                   Try the signature regional dish. (~$15–25 pp)
        Tip: Download an offline map before landing.

        ─────────────────────────────────────────────────────────────
        Day 2 — Culture & History
        ─────────────────────────────────────────────────────────────
        Morning:   Visit the top heritage site or national museum (free–$12).
                   Arrive early to beat the crowds.
        Afternoon: Explore the historic old quarter on foot.
                   Stop at a traditional craft market.
        Evening:   Rooftop bar with panoramic city views.
                   Street food tour (~$10 pp).
        Tip: Wear comfortable walking shoes — you'll cover 8–10 km.

        ─────────────────────────────────────────────────────────────
        Day 3 — Nature & Outdoors
        ─────────────────────────────────────────────────────────────
        Morning:   Half-day excursion to the nearest natural attraction
                   (national park, beach, or viewpoint). (~$20 transport)
        Afternoon: Picnic lunch with scenic views.
                   Light hiking or boat ride depending on the landscape.
        Evening:   Return to the city. Relax at a spa or local bathhouse.
        Tip: Book transport the night before; taxis fill up quickly.

        ─────────────────────────────────────────────────────────────
        Day 4 — Local Life & Food
        ─────────────────────────────────────────────────────────────
        Morning:   Morning market visit at sunrise — fresh produce, spices,
                   local snacks. Photography heaven.
        Afternoon: Cooking class or street-food walking tour (~$35 pp).
        Evening:   Fine-dining experience at a celebrated local chef's restaurant.
                   Reserve in advance. (~$40–60 pp)

        ─────────────────────────────────────────────────────────────
        Day 5 — Day Trip
        ─────────────────────────────────────────────────────────────
        Full Day:  Day trip to a nearby town, ruins, or island.
                   Hire a private guide for deeper insights (~$50/day).
                   Pack water, sunscreen, and a light jacket.
        Evening:   Back in the city by 7 pm. Rest or a casual dinner.

        ─────────────────────────────────────────────────────────────
        Day 6 — Art, Shopping & Leisure
        ─────────────────────────────────────────────────────────────
        Morning:   Contemporary art gallery or cultural centre.
        Afternoon: Browse boutique shops and local artisan stores.
                   Pick up authentic souvenirs (avoid tourist traps near
                   main squares).
        Evening:   Live music venue or traditional performance show.
                   (~$15–30 ticket)

        ─────────────────────────────────────────────────────────────
        Day 7 — Slow Morning & Departure
        ─────────────────────────────────────────────────────────────
        Morning:   Leisurely breakfast at a café loved by locals.
                   Last-minute stroll or revisit a favourite spot.
        Afternoon: Check out, head to the airport/station.
                   Allow 2–3 hrs before international flights.

        ─────────────────────────────────────────────────────────────
        ACCOMMODATION SUGGESTIONS ({budget} budget)
        ─────────────────────────────────────────────────────────────
        • Budget:   Hostel or guesthouse — $20–40/night
        • Moderate: Boutique hotel near city centre — $70–130/night
        • Comfort:  4-star hotel with breakfast included — $130–220/night
        • Luxury:   5-star resort or design hotel — $250+/night

        ─────────────────────────────────────────────────────────────
        TRANSPORT TIPS
        ─────────────────────────────────────────────────────────────
        • Get a multi-day public transport card on Day 1.
        • Use ride-hailing apps for late-night travel.
        • Consider renting a scooter or bicycle for day trips.

        ─────────────────────────────────────────────────────────────
        PACKING ESSENTIALS
        ─────────────────────────────────────────────────────────────
        ✓ Universal power adapter      ✓ Reusable water bottle
        ✓ Light rain jacket            ✓ Comfortable walking shoes
        ✓ Sunscreen SPF 50+            ✓ Small daypack
        ✓ Offline maps downloaded      ✓ Travel insurance docs

        ─────────────────────────────────────────────────────────────
        LOCAL CUSTOMS & TIPS
        ─────────────────────────────────────────────────────────────
        • Always carry a small amount of local cash.
        • Learn 5 basic phrases — locals deeply appreciate the effort.
        • Dress modestly when visiting religious or heritage sites.
        • Negotiate politely at markets; it is expected and respected.

        ════════════════════════════════════════════════════════════
        To generate a REAL AI itinerary using IBM Granite LLM:
        1. Copy travel_planner/.env.example → travel_planner/.env
        2. Add your WATSONX_API_KEY and WATSONX_PROJECT_ID
        3. Restart the server — this message will disappear
        ════════════════════════════════════════════════════════════
    """).strip()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"demo_mode": DEMO_MODE, "model": GRANITE_MODEL_ID})


@app.route("/generate", methods=["POST"])
def generate_itinerary():
    try:
        data = request.get_json()
        if not data or not data.get("destination"):
            return jsonify({"error": "Destination is required."}), 400

        if DEMO_MODE:
            itinerary_text = demo_itinerary(data)
        else:
            model  = get_watsonx_model()
            prompt = build_itinerary_prompt(data)
            response = model.generate_text(prompt=prompt)

            if isinstance(response, dict):
                itinerary_text = (
                    response.get("results", [{}])[0].get("generated_text", "")
                    or response.get("generated_text", "")
                )
            else:
                itinerary_text = str(response)

            if not itinerary_text.strip():
                return jsonify({"error": "No itinerary was generated. Please try again."}), 500

        return jsonify({
            "success":     True,
            "itinerary":   itinerary_text.strip(),
            "destination": data.get("destination"),
            "duration":    data.get("duration"),
            "demo_mode":   DEMO_MODE,
        })

    except Exception as exc:
        app.logger.error("Error generating itinerary: %s", exc)
        return jsonify({"error": f"Failed to generate itinerary: {str(exc)}"}), 500


@app.route("/destinations", methods=["GET"])
def popular_destinations():
    destinations = [
        {"name": "Paris, France",         "emoji": "🗼", "tag": "Romance & Culture"},
        {"name": "Tokyo, Japan",           "emoji": "🗾", "tag": "Tech & Tradition"},
        {"name": "New York, USA",          "emoji": "🗽", "tag": "Urban Adventure"},
        {"name": "Bali, Indonesia",        "emoji": "🌴", "tag": "Tropical Escape"},
        {"name": "Rome, Italy",            "emoji": "🏛️", "tag": "History & Food"},
        {"name": "Cape Town, South Africa","emoji": "🌍", "tag": "Nature & Wildlife"},
        {"name": "Sydney, Australia",      "emoji": "🦘", "tag": "Sun & Surf"},
        {"name": "Machu Picchu, Peru",     "emoji": "🏔️", "tag": "Ancient Wonders"},
    ]
    return jsonify(destinations)


if __name__ == "__main__":
    mode_label = "DEMO" if DEMO_MODE else "LIVE (IBM Granite)"
    print(f"\n  AI Travel Planner — {mode_label} mode")
    print(f"  Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
