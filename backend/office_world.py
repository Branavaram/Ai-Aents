"""
Office World — a visual floor plan where agents WALK around.

Agents can:
  - sit at their desk (idle)
  - walk to another agent's desk (passing work)
  - think with sparkles (working)
  - speak with a bubble (talking)
"""
import streamlit.components.v1 as components
from team import TEAM


# Fixed "home" desk positions on the office floor (x%, y%)
DESKS = {
    "alex":   {"x": 50, "y": 20, "label": "Alex 🧑‍💼 (Lead)"},
    "priya":  {"x": 18, "y": 60, "label": "Priya 👩‍💻"},
    "jake":   {"x": 36, "y": 60, "label": "Jake 👨‍💻"},
    "sam":    {"x": 62, "y": 60, "label": "Sam 🛡️"},
    "luna":   {"x": 82, "y": 60, "label": "Luna 📚"},
}


def render_office_world(
    agent_positions: dict = None,
    agent_statuses: dict = None,
    current_speaker: str = None,
    walking_to: dict = None,       # {"priya": "alex"} → Priya walking toward Alex
    speech_bubbles: dict = None,   # {"priya": "Found 3 bugs!"}
    height: int = 500,
):
    positions = {}
    for key in TEAM:
        if agent_positions and key in agent_positions:
            positions[key] = agent_positions[key]
        elif walking_to and key in walking_to:
            # mid-journey — show them at the target
            target_key = walking_to[key]
            tgt = DESKS.get(target_key, DESKS["alex"])
            # position them slightly offset from the target so avatars don't overlap
            positions[key] = {"x": tgt["x"] - 10, "y": tgt["y"] + 5}
        else:
            positions[key] = {"x": DESKS[key]["x"], "y": DESKS[key]["y"]}

    statuses = agent_statuses or {}
    bubbles = speech_bubbles or {}

    # Rooms / landmarks
    rooms_html = """
    <div class="room" style="left:3%; top:3%; width:28%; height:22%;">
        <span class="room-label">🪑 Meeting Room</span>
    </div>
    <div class="room" style="right:3%; top:3%; width:22%; height:22%;">
        <span class="room-label">☕ Coffee</span>
    </div>
    <div class="brain-badge">
        <span>🧠</span>
        <div class="brain-label">Shared Brain</div>
    </div>
    """

    avatars_html = ""
    for key, t in TEAM.items():
        pos = positions[key]
        status = statuses.get(key, "idle")
        bubble_text = bubbles.get(key, "")

        if status == "working":
            glow = f"box-shadow: 0 0 25px {t['color']}, 0 0 50px {t['color']}60;"
            anim = "animation: bounce 0.5s ease-in-out infinite alternate;"
            indicator = f'<div class="indicator ind-working" style="background:{t["color"]};">⚡</div>'
            sparkles = '<div class="sparkle s1">✨</div><div class="sparkle s2">✨</div><div class="sparkle s3">✨</div>'
        elif status == "walking":
            glow = f"box-shadow: 0 0 20px {t['color']};"
            anim = "animation: walkStep 0.3s ease-in-out infinite;"
            indicator = '<div class="indicator ind-walking">🏃</div>'
            sparkles = ""
        elif status == "talking":
            glow = f"box-shadow: 0 0 25px {t['color']};"
            anim = "animation: wiggle 0.4s ease-in-out infinite;"
            indicator = '<div class="indicator ind-talking">💬</div>'
            sparkles = ""
        elif status == "done":
            glow = "box-shadow: 0 0 20px #22c55e;"
            anim = ""
            indicator = '<div class="indicator ind-done">✅</div>'
            sparkles = ""
        else:  # idle
            glow = ""
            anim = ""
            indicator = ""
            sparkles = ""

        bubble_html = ""
        if bubble_text:
            bubble_html = f"""
            <div class="speech-bubble" style="border-color:{t['color']};">
                {bubble_text}
                <div class="bubble-tail" style="border-top-color:{t['color']};"></div>
            </div>
            """

        highlight = f"border: 3px solid {t['color']};" if current_speaker == key else ""

        avatars_html += f"""
        <div class="agent" style="left:{pos['x']}%; top:{pos['y']}%;">
            {bubble_html}
            <div class="avatar-ring" style="{glow} {anim} {highlight}">
                <div class="avatar-face">{t['emoji']}</div>
                {sparkles}
                {indicator}
            </div>
            <div class="agent-name" style="color:{t['color']};">{t['name']}</div>
        </div>
        """

    # Draw walking-path lines
    paths_html = ""
    if walking_to:
        for from_key, to_key in walking_to.items():
            src = DESKS[from_key]
            tgt = DESKS[to_key]
            paths_html += f"""
            <svg class="path-svg">
                <line x1="{src['x']}%" y1="{src['y']}%"
                      x2="{tgt['x']}%" y2="{tgt['y']}%"
                      stroke="{TEAM[from_key]['color']}" stroke-width="2"
                      stroke-dasharray="4,6" opacity="0.6">
                    <animate attributeName="stroke-dashoffset"
                             from="0" to="20" dur="0.8s" repeatCount="indefinite"/>
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
            radial-gradient(ellipse at top, #1e293b 0%, #0f172a 70%),
            repeating-linear-gradient(0deg, transparent 0 50px, rgba(148,163,184,0.04) 50px 51px),
            repeating-linear-gradient(90deg, transparent 0 50px, rgba(148,163,184,0.04) 50px 51px);
        border-radius: 20px;
        border: 1px solid #334155;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-shadow: inset 0 4px 20px rgba(0,0,0,0.3);
    }}

    .office-world::before {{
        content: '🏢  THE OFFICE FLOOR';
        position: absolute;
        top: 14px; left: 50%;
        transform: translateX(-50%);
        color: #64748b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 4px;
        z-index: 1;
    }}

    .room {{
        position: absolute;
        background: rgba(100, 116, 139, 0.06);
        border: 1px dashed rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .room-label {{
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
    }}

    .brain-badge {{
        position: absolute;
        left: 50%; top: 38%;
        transform: translateX(-50%);
        width: 70px; height: 70px;
        background: radial-gradient(circle, rgba(168,85,247,0.3) 0%, rgba(168,85,247,0.1) 70%);
        border: 2px solid rgba(168, 85, 247, 0.5);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: brainPulse 2.5s ease-in-out infinite;
        z-index: 1;
    }}

    .brain-badge span {{ font-size: 30px; }}

    .brain-label {{
        position: absolute;
        bottom: -22px;
        left: 50%;
        transform: translateX(-50%);
        color: #c084fc;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        white-space: nowrap;
    }}

    @keyframes brainPulse {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(168,85,247,0.3); }}
        50% {{ box-shadow: 0 0 40px rgba(168,85,247,0.6); }}
    }}

    .agent {{
        position: absolute;
        transform: translate(-50%, -50%);
        text-align: center;
        transition: left 1.5s cubic-bezier(0.4, 0.2, 0.2, 1),
                    top  1.5s cubic-bezier(0.4, 0.2, 0.2, 1);
        z-index: 3;
    }}

    .avatar-ring {{
        position: relative;
        width: 64px; height: 64px;
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
        border: 2px solid #334155;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        transition: all 0.3s ease;
    }}

    .avatar-face {{ font-size: 34px; line-height: 1; }}

    .indicator {{
        position: absolute;
        top: -6px; right: -6px;
        width: 24px; height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        border: 2px solid #0f172a;
    }}

    .ind-working {{ animation: ping 1s ease-in-out infinite; }}
    .ind-walking {{ background: #60a5fa; }}
    .ind-talking {{ background: #22c55e; }}
    .ind-done    {{ background: #22c55e; }}

    .sparkle {{
        position: absolute;
        font-size: 12px;
        pointer-events: none;
        animation: sparkleFloat 1.5s ease-in-out infinite;
    }}
    .s1 {{ top: -8px; left: -10px; animation-delay: 0s; }}
    .s2 {{ top: 20px; right: -14px; animation-delay: 0.5s; }}
    .s3 {{ bottom: -8px; left: 50%; animation-delay: 1s; }}

    @keyframes sparkleFloat {{
        0%, 100% {{ opacity: 0; transform: scale(0.5) translateY(0); }}
        50% {{ opacity: 1; transform: scale(1) translateY(-8px); }}
    }}

    .agent-name {{
        margin-top: 8px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}

    .speech-bubble {{
        position: absolute;
        bottom: 85px;
        left: 50%;
        transform: translateX(-50%);
        background: #1e293b;
        border: 2px solid;
        border-radius: 12px;
        padding: 10px 14px;
        color: #f1f5f9;
        font-size: 12px;
        max-width: 220px;
        min-width: 100px;
        text-align: left;
        animation: bubbleIn 0.4s ease;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        z-index: 4;
    }}

    .bubble-tail {{
        position: absolute;
        bottom: -10px; left: 50%;
        transform: translateX(-50%);
        width: 0; height: 0;
        border-left: 9px solid transparent;
        border-right: 9px solid transparent;
        border-top: 10px solid;
    }}

    .path-svg {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        pointer-events: none;
        z-index: 1;
    }}

    @keyframes bounce {{
        from {{ transform: translateY(0); }}
        to   {{ transform: translateY(-8px); }}
    }}

    @keyframes walkStep {{
        0%, 100% {{ transform: translateY(0) rotate(-2deg); }}
        50% {{ transform: translateY(-4px) rotate(2deg); }}
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

    @keyframes bubbleIn {{
        from {{ opacity: 0; transform: translateX(-50%) translateY(10px) scale(0.9); }}
        to {{ opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }}
    }}
    </style>

    <div class="office-world">
        {rooms_html}
        {paths_html}
        {avatars_html}
    </div>
    """

    components.html(html, height=height + 20, scrolling=False)
