/* ── Destination Cards ─────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  loadDestinations();
  setupChips();
  setupForm();
  setupClearBtn();
  setupCopyBtn();
});

// ── Popular destinations ─────────────────────────────────────────────────────
async function loadDestinations() {
  const grid = document.getElementById("destinations-grid");
  try {
    const res   = await fetch("/destinations");
    const dests = await res.json();
    grid.innerHTML = dests.map(d => `
      <button class="dest-card" data-name="${d.name}" tabindex="0" aria-label="Select ${d.name}">
        <span class="dest-emoji">${d.emoji}</span>
        <span class="dest-name">${d.name}</span>
        <span class="dest-tag">${d.tag}</span>
      </button>`).join("");

    grid.querySelectorAll(".dest-card").forEach(card => {
      card.addEventListener("click", () => {
        const nameField = document.getElementById("destination");
        nameField.value = card.dataset.name;
        nameField.focus();
        // Highlight selection briefly
        card.style.borderColor = "var(--accent)";
        setTimeout(() => card.style.borderColor = "", 1500);
        document.querySelector(".form-card").scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  } catch {
    grid.innerHTML = `<p style="color:var(--muted);font-size:.88rem;grid-column:1/-1">
      Could not load destinations.</p>`;
  }
}

// ── Interest chips toggle ─────────────────────────────────────────────────────
function setupChips() {
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("selected");
    });
  });
}

// ── Form submission ───────────────────────────────────────────────────────────
function setupForm() {
  document.getElementById("planner-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const destination = document.getElementById("destination").value.trim();
    if (!destination) {
      showError("Please enter a destination before generating.");
      return;
    }

    const interests = [...document.querySelectorAll(".chip.selected")]
      .map(c => c.querySelector("input").value);

    const payload = {
      destination,
      duration:             document.getElementById("duration").value,
      travelers:            document.getElementById("travelers").value,
      travel_style:         document.getElementById("travel_style").value,
      budget:               document.getElementById("budget").value,
      start_date:           document.getElementById("start_date").value || "flexible",
      special_requirements: document.getElementById("special_requirements").value.trim() || "none",
      interests,
    };

    showLoading(true);
    animateLoadingSteps();

    try {
      const res  = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok || data.error) {
        throw new Error(data.error || "Unknown error");
      }

      renderItinerary(data);
    } catch (err) {
      showError(err.message || "Failed to generate itinerary. Please try again.");
    } finally {
      showLoading(false);
    }
  });
}

// ── Render itinerary ──────────────────────────────────────────────────────────
function renderItinerary({ itinerary, destination, duration }) {
  const section = document.getElementById("result-section");
  const output  = document.getElementById("itinerary-output");
  const title   = document.getElementById("result-title");

  title.textContent = `Your ${duration}-Day Itinerary — ${destination}`;

  // Light markdown-like formatting
  const formatted = itinerary
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^(Day \d+[:\-–].+)$/gm, "<h3>$1</h3>")
    .replace(/^#{1,3} (.+)$/gm,       "<h3>$1</h3>")
    .replace(/\n/g, "<br />");

  output.innerHTML = formatted;

  section.classList.remove("hidden");
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Clear form ────────────────────────────────────────────────────────────────
function setupClearBtn() {
  document.getElementById("clear-btn").addEventListener("click", () => {
    document.getElementById("planner-form").reset();
    document.querySelectorAll(".chip.selected").forEach(c => c.classList.remove("selected"));
    document.getElementById("result-section").classList.add("hidden");
    document.getElementById("destination").focus();
  });
}

// ── Copy button ───────────────────────────────────────────────────────────────
function setupCopyBtn() {
  document.getElementById("copy-btn").addEventListener("click", async () => {
    const text = document.getElementById("itinerary-output").innerText;
    try {
      await navigator.clipboard.writeText(text);
      const btn = document.getElementById("copy-btn");
      const original = btn.innerHTML;
      btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
      btn.style.color = "var(--success)";
      setTimeout(() => { btn.innerHTML = original; btn.style.color = ""; }, 2000);
    } catch {
      showError("Could not copy to clipboard.");
    }
  });
}

// ── Loading state ─────────────────────────────────────────────────────────────
let stepTimer = null;

function showLoading(show) {
  const overlay = document.getElementById("loading-overlay");
  const btn     = document.getElementById("submit-btn");
  overlay.classList.toggle("hidden", !show);
  btn.disabled = show;
  if (!show && stepTimer) {
    clearInterval(stepTimer);
    stepTimer = null;
    resetLoadingSteps();
  }
}

function animateLoadingSteps() {
  const steps = document.querySelectorAll(".step");
  let current = 0;
  steps.forEach(s => { s.classList.remove("active", "done"); });
  steps[0].classList.add("active");

  stepTimer = setInterval(() => {
    if (current < steps.length - 1) {
      steps[current].classList.remove("active");
      steps[current].classList.add("done");
      current++;
      steps[current].classList.add("active");
    }
  }, 2200);
}

function resetLoadingSteps() {
  document.querySelectorAll(".step").forEach(s => s.classList.remove("active", "done"));
}

// ── Error toast ───────────────────────────────────────────────────────────────
let toastTimer = null;

function showError(msg) {
  const toast = document.getElementById("error-toast");
  document.getElementById("error-msg").textContent = msg;
  toast.classList.remove("hidden");
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 5000);
}
