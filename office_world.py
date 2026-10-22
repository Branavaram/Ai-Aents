"""
Office World — a visual floor plan where agents walk around.

Each agent moves toward whoever they're currently talking to.
"""
import json
import streamlit.components.v1 as components
from team import TEAM


# Fixed "home" desk positions on the office floor (x%, y%)
DESKS = {
    "alex":   {"x": 50, "y": 15, "label": "Alex's Desk 🧑‍💼"},
    "priya":  {"x": 20, "y": 55, "label": "Priya's Desk 👩‍💻"},
    "jake":   {"x": 40, "y": 55, "label": "Jake's Desk 👨‍💻"},
    "sam":    {"x": 65, "y": 55, "label": "Sam's Desk 🛡️"},
    "luna":   {"x": 85, "y": 55, "label": "Luna's Desk 📚"},
}


def render_office_world(agent_positions: dict = None,
                        agent_statuses: dict = None,
                        current_speaker: str = None,
                        height: int = 500):
    """
    Render the office floor.

    agent_positions: optional override for live positions {"alex": {"x": 50, "y": 30}, ...}
                     if None, uses DESKS.
    agent_statuses:  {"alex": "working" | "idle" | "talking"}
    current_speaker: agent key who's currently speaking (gets a highlight)
    """
    positions = agent_positions or {k: {"x": DESKS[k]["x"], "y": DESKS[k]["y"]} for k in DESKS}
    statuses = agent_statuses or {}

    # Furniture / landmarks
    rooms_html = """
    <div class="room meeting-room" style="left:5%; top:5%; width:30%; height:20%;">
        <span class="room-label">🪑 Meeting Room</span>
    </div>
    <div class="room coffee" style="right:5%; top:5%; width:25%; height:20%;">
        <span class="room-label">☕ Coffee Corner</span>
    </div>
    <div class="room brain" style="left:50%; top:30%; width:60px; height:60px; transform:translateX(-50%); border-radius:50%; display:flex; align-items:center; justify-content:center;">
        <span style="font-size:28px;">🧠</span>
    </div>
    """

    # Agent avatars (positioned absolutely)
    avatars_html = ""
    for key, t in TEAM.items():
        pos = positions.get(key, {"x": DESKS[key]["x"], "y": DESKS[key]["y"]})
        status = statuses.get(key, "idle")

        # Status visuals
        if status == "working":
            glow = f"box-shadow: 0 0 25px {t['color']}, 0 0 50px {t['color']}80;"
            anim = "animation: bounce 0.5s ease-in-out infinite alternate;"
            indicator = f'<div class="indicator working-ind" style="background:{t["color"]};">⚡</div>'
        elif status == "talking":
            glow = f"box-shadow: 0 0 25px {t['color']};"
            anim = "animation: wiggle 0.3s ease-in-out infinite;"
            indicator = f'<div class="indicator talking-ind">💬</div>'
        elif status == "done":
            glow = "box-shadow: 0 0 20px #22c55e;"
            anim = ""
            indicator = '<div class="indicator done-ind">✅</div>'
        else:  # idle
            glow = ""
            anim = ""
            indicator = ""

        highlight = ""
        if current_speaker == key:
            highlight = f"border: 3px solid {t['color']}; transform: scale(1.1);"

        avatars_html += f"""
        <div class="agent" style="left:{pos['x']}%; top:{pos['y']}%;">
            <div class="desk-label">{DESKS[key]['label']}</div>
            <div class="avatar-wrap" style="{glow} {anim} {highlight}" onclick="selectAgent('{key}')">
                <div class="face">{t['emoji']}</div>
                {indicator}
            </div>
            <div class="agent-name" style="color:{t['color']};">{t['name']}</div>
        </div>
        """

    # Draw a line between speakers if someone is talking
    line_html = ""
    if current_speaker and current_speaker in positions:
        src = positions[current_speaker]
        # draw to Alex (manager) as default target
        if current_speaker != "alex":
            tgt = positions.get("alex", {"x": 50, "y": 15})
            line_html = f"""
            <svg class="line-svg">
                <line x1="{src['x']}%" y1="{src['y']}%" x2="{tgt['x']}%" y2="{tgt['y']}%"
                      stroke="{TEAM[current_speaker]['color']}" stroke-width="2"
                      stroke-dasharray="5,5">
                    <animate attributeName="stroke-dashoffset" from="0" to="20"
                             dur="0.6s" repeatCount="indefinite"/>
                </line>
            </svg>
            """

    html = f"""
    <style>
    .office-world {{
        position: relative;
        width: 100%;
        height: {height}px;
        background:
            linear-gradient(135deg, #1e293b 0%, #0f172a 100%),
            repeating-linear-gradient(0deg, transparent 0 40px, rgba(148,163,184,0.05) 40px 41px),
            repeating-linear-gradient(90deg, transparent 0 40px, rgba(148,163,184,0.05) 40px 41px);
        border-radius: 16px;
        border: 1px solid #334155;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    .office-world::before {{
        content: '🏢 THE OFFICE FLOOR';
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        color: #64748b;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 3px;
        z-index: 1;
    }}

    .room {{
        position: absolute;
        background: rgba(100, 116, 139, 0.08);
        border: 1px dashed rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .room-label {{
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
    }}

    .brain {{
        background: rgba(168, 85, 247, 0.15) !important;
        border: 2px solid rgba(168, 85, 247, 0.5) !important;
        animation: brainPulse 2s ease-in-out infinite;
    }}

    @keyframes brainPulse {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(168,85,247,0.3); }}
        50% {{ box-shadow: 0 0 30px rgba(168,85,247,0.6); }}
    }}

    .agent {{
        position: absolute;
        transform: translate(-50%, -50%);
        text-align: center;
        transition: all 0.8s cubic-bezier(0.4, 0.2, 0.2, 1);
        z-index: 2;
    }}

    .avatar-wrap {{
        position: relative;
        width: 60px;
        height: 60px;
        background: rgba(30, 41, 59, 0.9);
        border: 2px solid #334155;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0 auto;
    }}

    .face {{ font-size: 32px; }}

    .indicator {{
        position: absolute;
        top: -8px;
        right: -8px;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        border: 2px solid #0f172a;
    }}

    .working-ind {{ animation: ping 1s ease-in-out infinite; }}
    .talking-ind {{ background: #22c55e; }}
    .done-ind    {{ background: #22c55e; }}

    .agent-name {{
        margin-top: 6px;
        font-size: 12px;
        font-weight: 700;
    }}

    .desk-label {{
        position: absolute;
        bottom: 60px;
        left: 50%;
        transform: translateX(-50%);
        color: #475569;
        font-size: 9px;
        white-space: nowrap;
    }}

    .line-svg {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
    }}

    @keyframes bounce {{
        from {{ transform: translateY(0); }}
        to   {{ transform: translateY(-8px); }}
    }}

    @keyframes wiggle {{
        0%, 100% {{ transform: rotate(0deg); }}
        25% {{ transform: rotate(-5deg); }}
        75% {{ transform: rotate(5deg); }}
    }}

    @keyframes ping {{
        0% {{ transform: scale(1); opacity: 1; }}
        75% {{ transform: scale(1.4); opacity: 0; }}
        100% {{ transform: scale(1.4); opacity: 0; }}
    }}
    </style>

    <div class="office-world">
        {rooms_html}
        {line_html}
        {avatars_html}
    </div>

    <script>
    function selectAgent(key) {{
        // Scroll parent window to the clicked agent's info panel
        window.parent.postMessage({{ type: 'agent_click', agent: key }}, '*');
    }}
    </script>
    """

    components.html(html, height=height + 20, scrolling=False)
