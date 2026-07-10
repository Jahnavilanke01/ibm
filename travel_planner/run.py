"""Launcher — run this to start the Travel Planner server."""
import sys, os

# Make sure imports resolve whether launched from inside or outside the folder
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
os.chdir(here)

from app import app, DEMO_MODE

mode = "DEMO (template itinerary)" if DEMO_MODE else "LIVE — IBM Granite LLM"
print(f"\n  AI Travel Planner starting in {mode} mode")
print("  Open http://127.0.0.1:5000 in your browser\n")
app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False)
