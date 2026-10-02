# 🤖 TaskPilot AI

> An AI-powered task automation agent that can plan, execute, and verify real-world tasks using tools and external services.

## ✨ Overview

TaskPilot AI is an intelligent AI agent designed to understand user requests, create execution plans, use appropriate tools, and verify the results.

The project combines AI reasoning, tool calling, memory, browser automation, web search, file management, and external service integrations into one task-oriented agent.

---

## 🚀 Features

- 🤖 AI-powered task planning
- 🧠 Short-term and persistent memory
- 🔧 Tool calling
- 🧮 Calculator
- 🌐 Web search
- 🌍 Browser automation
- 📁 File management
- 📧 Gmail integration
- 🗄️ Task database
- ✅ Task verification
- 👤 Human confirmation for sensitive actions
- 📝 Response formatting
- 🔄 Autonomous task execution

---

## 🏗️ Architecture

```text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    FastAPI      │
                         │     api.py      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    AI Agent     │
                         │    agent.py     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Planner     │
                         │   planner.py    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Executor     │
                         │   executor.py   │
                         └────────┬────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
          ┌────────────┐   ┌────────────┐   ┌────────────┐
          │ Calculator │   │  Browser   │   │    Gmail   │
          └────────────┘   └────────────┘   └────────────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Verifier     │
                         │  verifier.py    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Response     │
                         │    Formatter    │
                         └─────────────────┘