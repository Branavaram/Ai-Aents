"""
Slack-style chat panel for the AI dev team.
Shows messages from each agent as styled bubbles.
"""
import streamlit.components.v1 as components
from team import TEAM


def render_chat(messages: list, height: int = 500):
    """
    Render chat messages Slack-style.
    messages: list of dicts: [{"agent": "priya", "text": "...", "time": "14:32"}, ...]
    """
    msg_html = ""
    for msg in messages:
        agent_key = msg.get("agent", "alex")
        agent = TEAM.get(agent_key, TEAM["alex"])
        text = msg.get("text", "")
        time = msg.get("time", "")

        msg_html += f"""
        <div class="msg">
            <div class="avatar" style="background:{agent['color']}25;border-color:{agent['color']};">
                {agent['emoji']}
            </div>
            <div class="body">
                <div class="header">
                    <span class="name" style="color:{agent['color']};">{agent['name']}</span>
                    <span class="role">{agent['role']}</span>
                    <span class="time">{time}</span>
                </div>
                <div class="text">{text}</div>
            </div>
        </div>
        """

    html = f"""
    <style>
    .chat-container {{
        background: #0f172a;
        border-radius: 12px;
        border: 1px solid #334155;
        padding: 16px;
        max-height: {height}px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    .chat-header {{
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #1e293b;
    }}

    .msg {{
        display: flex;
        gap: 12px;
        padding: 10px 0;
        animation: slideIn 0.3s ease;
    }}

    .msg + .msg {{ border-top: 1px solid #1e293b; }}

    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        border: 2px solid;
        flex-shrink: 0;
    }}

    .body {{ flex: 1; min-width: 0; }}

    .header {{
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-bottom: 4px;
    }}

    .name {{ font-size: 14px; font-weight: 700; }}
    .role {{ font-size: 11px; color: #64748b; font-weight: 500; }}
    .time {{ font-size: 11px; color: #475569; margin-left: auto; }}

    .text {{
        font-size: 13px;
        color: #e2e8f0;
        line-height: 1.5;
        word-wrap: break-word;
    }}

    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-10px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    .empty {{
        color: #475569;
        font-size: 13px;
        text-align: center;
        padding: 40px 20px;
        font-style: italic;
    }}
    </style>

    <div class="chat-container">
        <div class="chat-header">💬 #team-chat</div>
        {msg_html if msg_html else '<div class="empty">No messages yet. Run a review to see the team talk!</div>'}
    </div>
    """

    components.html(html, height=height + 60, scrolling=False)
