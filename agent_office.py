"""
Animated agent office — HTML/CSS component for Streamlit.
Shows agents as avatars that move, glow, and show thoughts.
"""
import streamlit.components.v1 as components


def render_office(agent_states: dict, height: int = 400):
    """
    Render the animated office.

    agent_states: dict like
      {
        "reviewer":   {"status": "working", "thought": "Checking line 42..."},
        "security":   {"status": "waiting", "thought": ""},
        "summarizer": {"status": "idle",    "thought": ""},
      }

    status options: "idle" | "working" | "done" | "waiting"
    """
    # Agent definitions
    agents = [
        {"key": "reviewer",   "name": "Reviewer",   "emoji": "🧑‍💻", "x": 15, "color": "#60a5fa"},
        {"key": "security",   "name": "Security",   "emoji": "🛡️",   "x": 50, "color": "#f87171"},
        {"key": "summarizer", "name": "Summarizer", "emoji": "📋",   "x": 85, "color": "#34d399"},
    ]

    # Build each agent's HTML
    agent_html = ""
    for a in agents:
        state = agent_states.get(a["key"], {"status": "idle", "thought": ""})
        status = state.get("status", "idle")
        thought = state.get("thought", "")

        # Visual states
        if status == "working":
            glow = f"box-shadow: 0 0 30px {a['color']}, 0 0 60px {a['color']};"
            anim = "animation: bounce 0.6s infinite alternate;"
            opacity = "1"
        elif status == "done":
            glow = f"box-shadow: 0 0 20px #22c55e;"
            anim = ""
            opacity = "1"
        elif status == "waiting":
            glow = ""
            anim = "animation: pulse 1.5s infinite;"
            opacity = "0.6"
        else:  # idle
            glow = ""
            anim = ""
            opacity = "0.4"

        bubble = ""
        if thought:
            bubble = f"""
            <div class="bubble" style="border-color: {a['color']};">
                {thought}
                <div class="bubble-tail" style="border-top-color: {a['color']};"></div>
            </div>
            """

        agent_html += f"""
        <div class="agent" style="left: {a['x']}%;">
            {bubble}
            <div class="avatar" style="{glow} {anim} opacity: {opacity};">
                {a['emoji']}
            </div>
            <div class="name" style="color: {a['color']};">{a['name']}</div>
            <div class="status">{status}</div>
        </div>
        """

    # Draw lines between agents if one is passing to another
    lines_html = ""
    if agent_states.get("reviewer", {}).get("status") == "done" and \
       agent_states.get("security", {}).get("status") in ["working", "waiting"]:
        lines_html += '<div class="connection line1"></div>'
    if agent_states.get("security", {}).get("status") == "done" and \
       agent_states.get("summarizer", {}).get("status") in ["working", "waiting"]:
        lines_html += '<div class="connection line2"></div>'

    html = f"""
    <style>
    .office {{
        position: relative;
        width: 100%;
        height: {height}px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        border: 1px solid #334155;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    .office::before {{
        content: '🏢 Code Review Office';
        position: absolute;
        top: 12px;
        left: 20px;
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1px;
    }}

    .brain {{
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 20px;
        padding: 6px 12px;
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 12px;
        color: #c084fc;
        font-size: 12px;
        font-weight: 600;
    }}

    .agent {{
        position: absolute;
        bottom: 60px;
        transform: translateX(-50%);
        text-align: center;
        transition: all 0.5s ease;
    }}

    .avatar {{
        font-size: 60px;
        padding: 12px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
        display: inline-block;
        transition: all 0.3s ease;
    }}

    .name {{
        font-size: 14px;
        font-weight: 700;
        margin-top: 8px;
    }}

    .status {{
        font-size: 10px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }}

    .bubble {{
        position: relative;
        background: #1e293b;
        border: 2px solid;
        border-radius: 12px;
        padding: 8px 12px;
        color: #f1f5f9;
        font-size: 12px;
        max-width: 180px;
        margin: 0 auto 20px;
        animation: fadeIn 0.4s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}

    .bubble-tail {{
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 10px solid;
    }}

    .connection {{
        position: absolute;
        top: 50%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #22c55e, transparent);
        animation: flow 1.5s infinite;
    }}

    .line1 {{ left: 15%; width: 35%; }}
    .line2 {{ left: 50%; width: 35%; }}

    @keyframes bounce {{
        from {{ transform: translateY(0); }}
        to   {{ transform: translateY(-10px); }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes flow {{
        0% {{ opacity: 0; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    </style>

    <div class="office">
        <div class="brain">🧠 Shared Brain</div>
        {lines_html}
        {agent_html}
    </div>
    """

    components.html(html, height=height + 20)
