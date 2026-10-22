# 🧠 The Vault — Your AI Crew's Shared Brain

This folder is **memory** for your Code Review Crew. Every agent reads these files before reviewing code, so they know YOU — your style, your preferences, your past work.

## Structure

```
vault/
├── profile/                 ← About YOU as a developer
│   ├── coding_style.md      ← How you write code
│   └── pet_peeves.md        ← Things to NOT suggest
├── knowledge/               ← General technical knowledge
│   └── security_patterns.md ← OWASP, common vulns
├── projects/                ← Per-project context (add your own)
│   └── my_project.md        ← e.g. "Mark-XLVI uses Gemini"
└── reviews/                 ← Past reviews (auto-saved)
    └── 2026-10-22_login.md  ← YYYY-MM-DD_filename
```

## How To Make Agents Smarter
1. **Edit `profile/coding_style.md`** — the more specific, the better
2. **Edit `profile/pet_peeves.md`** when the crew annoys you with low-value suggestions
3. **Add project notes** in `projects/` for each project you work on
4. **Past reviews auto-save** so the crew doesn't repeat itself

## Open This In Obsidian (Optional)
Install Obsidian from obsidian.md → "Open vault" → pick this folder.
You'll see all notes with pretty formatting, backlinks, and search.
The crew works WITHOUT Obsidian too — it just reads the markdown files directly.
