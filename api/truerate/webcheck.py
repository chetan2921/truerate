"""A web check for creators bigger than anyone WLDD has booked: does any source state what this creator charges for a
reel? Gemini searches with Google. Only public facts about the creator go in, never a WLDD price."""

import re

PROMPT = """Search the web for what the Instagram creator @{handle}{name} ({followers} followers, {category}, India) charges for one sponsored Instagram reel.
Only use figures that a source states for this creator: a published rate card, an interview, an agency or marketplace listing, or a news report of a deal. Do not estimate from follower counts or general rate cards.
Answer in exactly these four lines:
FOUND: yes or no
LOW_INR: the lowest stated price for one reel in rupees as a plain integer, or none
HIGH_INR: the highest stated price for one reel in rupees as a plain integer, or none
SUMMARY: one sentence saying what the sources state, or that nothing was found"""


def _field(text: str, name: str) -> str:
    m = re.search(rf"^\s*{name}:\s*(.+)$", text, re.M | re.I)
    return m.group(1).strip() if m else ""


def _rupees(value: str) -> int | None:
    digits = value.replace(",", "").replace("₹", "").strip()
    return int(digits) if digits.isdigit() else None


def web_rate(llm, handle: str, full_name: str, followers: int, category: str) -> dict:
    """What the web states this creator charges per reel, with the pages behind it. A figure counts as found only when
    it is readable, plausible and sourced; otherwise the answer is that nothing was found."""
    size = f"about {followers / 1e5:.1f} lakh" if followers >= 1e5 else f"{followers:,}"
    reply = llm.search(PROMPT.format(handle=handle, name=f" ({full_name})" if full_name else "", followers=size, category=category or "creator"))
    text = reply.get("text") or ""
    low, high = _rupees(_field(text, "LOW_INR")), _rupees(_field(text, "HIGH_INR"))
    found = (_field(text, "FOUND").lower().startswith("yes") and low is not None and high is not None and 500 <= low <= high
             and bool(reply.get("sources")))
    return {"found": found, "low": low if found else None, "high": high if found else None,
            "summary": _field(text, "SUMMARY") or "No answer from the web search.", "sources": reply.get("sources", [])}
