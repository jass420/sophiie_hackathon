# Sophiie AI Agents Hackathon 2026

**Build the future of AI-human interaction.**

| | |
|---|---|
| **What** | A solo hackathon focused on AI agent interaction — voice, text, UX, and UI |
| **When** | February 14–15, 2026 (Saturday–Sunday) |
| **Where** | Virtual — participate from anywhere in Australia |
| **Prize** | **$5,000 AUD cash** (1st place) + job offers for top performers |
| **Format** | Solo only — show us what *you* can build |
| **Hacking Time** | 33 hours |

---

## The Challenge

**Design and build an AI agent with an exceptional interaction experience.**

We want to see how you think about the space between humans and AI. This is deliberately open-ended — you choose the problem, the modality, and the approach. What matters is the *interaction*.

Some directions to inspire you (not requirements):

- A voice agent that feels natural to talk to
- A text-based assistant with a thoughtful, intuitive UX
- A multi-modal agent that blends voice, text, and visual elements
- An agent that handles a complex workflow through conversation
- Something we haven't thought of yet

**You will be judged on innovation, technical execution, and how good the interaction feels** — not just whether the AI works, but whether a human would *want* to use it.

Use any tech stack. Use any AI provider. Use AI coding assistants. The only constraint is time.

---

## Schedule

All times are **AEST (Australian Eastern Standard Time, UTC+10 — Brisbane time)**.

### Saturday, February 14

| Time | Event |
|------|-------|
| **9:00 AM** | Kickoff — challenge explained, rules confirmed |
| **9:30 AM** | **Hacking begins** |
| 12:00 PM | Office hours / Q&A (optional, Discord) |
| 4:00 PM | Community check-in / progress sharing (optional, Discord) |

### Sunday, February 15

| Time | Event |
|------|-------|
| **6:00 PM** | **Submission deadline — hard cut-off, no exceptions** |

### After the Hackathon

| When | Event |
|------|-------|
| Feb 16 – Feb 28 | Judging period — judges review all submissions |
| ~Early March | Winners announced via livestream (details shared on Discord and Email) |

---

## Rules

### The Essentials

1. **Solo only** — one person per submission, no teams
2. **No pre-work** — all project code must be written during the hackathon window (after 9:30 AM AEST, Feb 14)
3. **Public GitHub repo** — your repository must be publicly visible at time of submission
4. **AI assistance is allowed** — Copilot, Claude, ChatGPT, Cursor, whatever you want. You still need to build it within the timeframe
5. **Must be functional** — your project must run and be demonstrable, not just a concept or slide deck
6. **One submission per person** — you may iterate, but submit one final project

### What You CAN Prepare Before Kickoff

- Research, planning, and brainstorming (on paper, in your head — just not in code)
- Setting up your development environment
- Reading documentation for tools/APIs you plan to use
- Creating accounts (GitHub, API providers, etc.)
- Watching tutorials

### What You CANNOT Do Before Kickoff

- Write any project code
- Create your project repository
- Fork/clone an existing project and modify it
- Build components, libraries, or templates specifically for your submission
- Start a project in a private repo then make it public later

### How We Verify

We will check:
- **Repository creation date** — must be after 9:30 AM AEST, Feb 14
- **Commit history** — should show natural progression, not a single massive commit
- **First commit timestamp** — must be after kickoff

**Red flags that will result in disqualification:**
- Repo created before the hackathon
- Single commit containing the entire project
- Commits timestamped before kickoff
- Evidence of code copied from a pre-existing private repo

---

## Submission Requirements

**Deadline: 6:00 PM AEST, Sunday February 15, 2026 — hard cut-off.**

To submit, you must complete **all** of the following:

1. **Public GitHub repo** — created after kickoff, with a clear commit history
2. **This README** — fill out the [Your Submission](#your-submission) section below
3. **Demo video** (2–5 minutes) — show your agent in action, explain your approach
4. **Working project** — judges must be able to understand and evaluate your agent from the repo + video

### How to Submit

1. Fork this repository
2. Build your project in the fork
3. Fill out the [Your Submission](#your-submission) section below
4. Record your demo video and add the link to your submission
5. Ensure your repo is **public** before 6:00 PM AEST Sunday
6. Submit your repo link via the submission form (link will be shared at kickoff)

---

## Judging Criteria

| Criteria | Weight | What We're Looking For |
|----------|--------|----------------------|
| **Interaction Design** | 30% | How intuitive, natural, and delightful is the human-AI interaction? Does it feel good to use? |
| **Innovation** | 25% | Novel approach, creative problem-solving, or a fresh take on agent interaction |
| **Technical Execution** | 25% | Code quality, architecture, reliability, completeness |
| **Presentation** | 20% | Demo quality, clarity of communication, ability to convey your vision |

### Judges

Sophiie senior engineers and CTO. Judging will take place over a 2-week period following the submission deadline.

---

## Prizes

| Place | Prize |
|-------|-------|
| **1st Place** | **$5,000 AUD cash** |
| **Top Performers** | Job offers or interview fast-tracks at Sophiie* |
| **All Finalists** | Consideration for current and future roles |

*\*Job offers and interview fast-tracks are entirely at the discretion of Sophiie and are not guaranteed.*

> Participants retain full ownership and IP of their submissions. Sophiie receives a non-exclusive license to review and evaluate submissions for judging purposes only.

---

## Your Submission

> **Instructions:** Fill out this section in your forked repo. This is what judges will see first.

### Participant

| Field | Your Answer |
|-------|-------------|
| **Name** | Jasnoor Singh |
| **University / Employer** | Gradianza (self employed)|

### Project

| Field | Your Answer |
|-------|-------------|
| **Project Name** | Roomie |
| **One-Line Description** | An AI interior design assistant that analyzes your room, searches Facebook Marketplace for affordable furniture, and messages sellers for you — all through voice or text. |
| **Demo Video Link** | |
| **Tech Stack** | React + TypeScript (Vite), Python + FastAPI, LangGraph, Playwright MCP, Tailwind CSS |
| **AI Provider(s) Used** | OpenAI GPT-5 (orchestrator + workers), OpenAI Whisper (speech-to-text), OpenAI TTS (text-to-speech) |

### About Your Project

#### What does it do?

Roomie is an AI interior design assistant that helps people furnish their homes beautifully and affordably using second-hand marketplaces. Upload a photo of your room, and Roomie analyzes the space — identifying the room type, dimensions, lighting, and current style — then suggests a color palette and furniture recommendations tailored to your taste and budget.

Once you approve the direction, Roomie dispatches parallel browser-based worker agents that autonomously search Facebook Marketplace in real-time using Playwright. These workers navigate the actual website, scan listing cards for titles, prices, and locations, and return their top picks. Roomie then curates the results, explains why each piece works for your space, and drafts personalized messages to sellers.

The entire flow — from room analysis to contacting sellers — happens through a single conversational interface with optional voice interaction. You can speak to Roomie and hear responses read aloud, making the experience feel like chatting with a knowledgeable interior designer friend.

#### How does the interaction work?

The user opens the app and is greeted by Roomie in a clean, glassmorphic chat interface. They can type or use the microphone button to speak — speech is transcribed via OpenAI Whisper and fed into the conversation. They upload a photo of their room, and Roomie responds with a detailed analysis including a visual color palette with hex codes.

Roomie asks about style preferences and budget (one question at a time to keep it conversational), then dispatches search tasks. Behind the scenes, two Playwright browser workers open separate Chromium windows and search Facebook Marketplace simultaneously. The user sees the agent working in real-time through a live browser preview panel.

When results come back, Roomie presents curated picks with prices, conditions, and reasons why each item fits. An approval card appears where the user can approve all items, select specific ones, or reject them. Each item includes a pre-drafted message to the seller. On approval, messaging workers automatically navigate to the listings and send the messages — no manual copy-pasting needed.

#### What makes it special?

**Real browser automation, not API scraping.** Roomie's workers actually open Chromium browsers and navigate Facebook Marketplace like a human would. This means it works with any marketplace without needing official APIs — and the user can watch it happen live through the browser preview panel.

**Orchestrator + Worker architecture with true parallelism.** The LangGraph-based system uses a project manager (orchestrator) that delegates to specialized browser workers running in parallel, each with their own isolated browser instance. This mirrors how a real design team would work — one person coordinates while others search.

**Full voice loop.** The app supports complete voice interaction — speak your request, hear the response. TTS is chunked by sentence for near-instant playback, so there's no awkward delay between the AI responding and speaking.

**Human-in-the-loop approval flow.** Nothing gets sent to sellers without explicit user approval. The graph literally pauses (using LangGraph's `interrupt()`) and waits for the user to review and approve before any messages go out.

#### How to run it

```bash
# Clone the repo
git clone https://github.com/jasnoorsingh/sophiie_hackathon.git
cd sophiie_hackathon

# Set up environment variables
cp .env.example .env
# Fill in: OPENAI_APIKEY, FB_EMAIL, FB_PASSWORD

# Install backend dependencies
pip install uv  # if not installed
uv sync

# Start Playwright MCP servers (two separate terminals or background)
npx @playwright/mcp@latest --port 3001 --no-sandbox --shared-browser-context --viewport-size 1920x1080 --user-data-dir /tmp/pw-user-data-a &
npx @playwright/mcp@latest --port 3002 --no-sandbox --shared-browser-context --viewport-size 1920x1080 --user-data-dir /tmp/pw-user-data-b &

# Start the backend
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the frontend
cd ../frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`. The frontend proxies API requests to the backend on port 8000.

#### Architecture / Technical Notes

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                  │
│  Chat UI · Voice (STT/TTS) · Browser Preview · UX   │
└──────────────────────┬──────────────────────────────┘
                       │ SSE streaming
┌──────────────────────▼──────────────────────────────┐
│                 Backend (FastAPI)                     │
│  /api/chat · /api/chat/resume · /api/voice/*         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              LangGraph State Machine                 │
│                                                      │
│  ┌─────────────┐    ┌──────────────┐                │
│  │ Orchestrator │───▶│ Tool Router  │                │
│  │   (GPT-5)   │◀───│              │                │
│  └─────────────┘    └──────┬───────┘                │
│                            │                         │
│              ┌─────────────┼─────────────┐          │
│              ▼             ▼             ▼          │
│        ┌──────────┐ ┌──────────┐ ┌────────────┐    │
│        │ Worker A  │ │ Worker B  │ │  Human     │    │
│        │ (search)  │ │ (search)  │ │  Approval  │    │
│        └─────┬─────┘ └─────┬─────┘ │ interrupt()│    │
│              │             │        └────────────┘    │
│              ▼             ▼                         │
│        ┌──────────┐ ┌──────────┐                    │
│        │Playwright│ │Playwright│                    │
│        │ MCP :3001│ │ MCP :3002│                    │
│        └──────────┘ └──────────┘                    │
│              │             │                         │
│              ▼             ▼                         │
│        ┌──────────┐ ┌──────────┐                    │
│        │Chromium A│ │Chromium B│                    │
│        └──────────┘ └──────────┘                    │
└─────────────────────────────────────────────────────┘
```

**Key decisions:**
- **LangGraph over raw LangChain** — the state machine with `interrupt()` enables true human-in-the-loop approval without hacky polling or WebSocket state management
- **Playwright MCP over Selenium/API scraping** — MCP provides a clean tool interface that LLMs can call directly, and Playwright handles modern JS-heavy sites like Facebook Marketplace
- **Dual MCP servers** — each worker gets its own browser process and user data directory for true parallel browsing without session conflicts
- **SSE streaming** — the backend streams partial responses to the frontend so the user sees the AI "typing" in real-time
- **Sentence-chunked TTS** — instead of waiting for the full response to synthesize, audio is split into ~150-char sentence chunks and played sequentially for near-instant voice feedback

---

## Code of Conduct

All participants must adhere to a standard of respectful, professional behavior. Harassment, discrimination, or disruptive behavior of any kind will result in immediate disqualification.

By participating, you agree to:
- Treat all participants, judges, and organizers with respect
- Submit only your own original work created during the hackathon
- Not interfere with other participants' work
- Follow the rules outlined in this document

---

## Communication & Support

- **Discord** — join the hackathon Discord server for announcements, Q&A, and community chat (link provided upon registration)
- **Office hours** — available during the event for technical questions

---

## FAQ

**Q: Can I use boilerplate / starter templates?**
A: You can use publicly available boilerplate (e.g., `create-react-app`, `Next.js` starter) as a starting point. You cannot use custom templates you built specifically for this hackathon before kickoff.

**Q: Can I use existing open-source libraries and APIs?**
A: Yes. You can use any publicly available libraries, frameworks, APIs, and services. The code *you* write must be created during the hackathon.

**Q: Do I need to be in Australia?**
A: Preferred but not strictly required. The hackathon is primarily targeted at Australian residents and students, but we won't turn away great talent.

**Q: Can I use AI coding tools like Copilot or Claude?**
A: Absolutely. Use whatever tools you want. The 33-hour time constraint is the great equalizer.

**Q: What if I can't finish?**
A: Submit what you have. A well-thought-out partial project with a great demo video can still score well. We're evaluating your thinking and skill, not just completion.

**Q: How will I know if I won?**
A: Winners will be announced via livestream approximately 2 weeks after the hackathon. All participants will be notified.

**Q: Can I keep working on my project after the deadline?**
A: You can continue developing after the hackathon, but **only the state of your repo at 6:00 PM AEST Sunday Feb 15 will be judged**. We will check commit timestamps.

---

## About Sophiie

Sophiie is an AI office manager for trades businesses — helping plumbers, electricians, builders, and other trade professionals run their operations with intelligent automation. We're a team that cares deeply about how humans interact with AI, and we're looking for people who think the same way.

[sophiie.com](https://sophiie.com)

---

**Good luck. Build something that makes us say "wow."**
