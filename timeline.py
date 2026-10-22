"""
Timeline view — shows all team actions chronologically.
"""
import streamlit.components.v1 as components
from team import TEAM


def render_timeline(events: list, height: int = 400):
    """
    events: list of dicts [{"agent": "priya", "action": "Reviewed login.py", "time": "14:32", "detail": "Found 3 bugs"}, ...]
    """
    items = ""
    for e in events:
        agent = TEAM.get(e.get("agent", "alex"), TEAM["alex"])
        action = e.get("action", "")
        time = e.get("time", "")
        detail = e.get("detail", "")

        items += f"""
        <div class="t-item">
            <div class="t-dot" style="background:{agent['color']};"></div>
            <div class="t-content">
                <div class="t-header">
                    <span class="t-time">{time}</span>
                    <span class="t-emoji">{agent['emoji']}</span>
                    <span class="t-name" style="color:{agent['color']};">{agent['name']}</span>
                </div>
                <div class="t-action">{action}</div>
                {f'<div class="t-detail">{detail}</div>' if detail else ''}
            </div>
        </div>
        """

    html = f"""
    <style>
    .timeline {{
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        max-height: {height}px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        position: relative;
    }}

    .timeline::before {{
        content: '📜 Activity Timeline';
        display: block;
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #1e293b;
    }}

    .t-item {{
        position: relative;
        padding: 10px 0 10px 24px;
        border-left: 2px solid #1e293b;
        margin-left: 8px;
        animation: fadeIn 0.4s ease;
    }}

    .t-dot {{
        position: absolute;
        left: -7px; top: 14px;
        width: 12px; height: 12px;
        border-radius: 50%;
        border: 2px solid #0f172a;
    }}

    .t-header {{ display: flex; align-items: center; gap: 8px; font-size: 12px; }}
    .t-time {{ color: #64748b; font-family: monospace; }}
    .t-emoji {{ font-size: 14px; }}
    .t-name {{ font-weight: 700; }}
    .t-action {{ color: #cbd5e1; font-size: 13px; margin-top: 4px; }}
    .t-detail {{ color: #64748b; font-size: 11px; margin-top: 2px; font-style: italic; }}

    .empty {{
        color: #475569;
        font-size: 12px;
        text-align: center;
        padding: 30px 10px;
        font-style: italic;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-5px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>

    <div class="timeline">
        {items if items else '<div class="empty">No activity yet.</div>'}
    </div>
    """

    components.html(html, height=height + 40, scrolling=False)
