# Multi-Agent Orchestration: Complete Learning Guide

**Author:** Saikrishna Paila
**Project:** Smart Recruiter Agent (Project 4 of 12 AI Projects 2026)

---

## Table of Contents

1. [What is Multi-Agent Orchestration?](#1-what-is-multi-agent-orchestration)
2. [Single Agent vs Multi-Agent](#2-single-agent-vs-multi-agent)
3. [Core Concepts](#3-core-concepts)
4. [Orchestration Patterns](#4-orchestration-patterns)
5. [Popular Frameworks Comparison](#5-popular-frameworks-comparison)
6. [Tools & Libraries](#6-tools--libraries)
7. [How Agents Communicate](#7-how-agents-communicate)
8. [Building Blocks](#8-building-blocks)
9. [Recommended Approach for Our Project](#9-recommended-approach-for-our-project)
10. [Implementation Plan](#10-implementation-plan)

---

## 1. What is Multi-Agent Orchestration?

### Definition
Multi-agent orchestration is a system where **multiple AI agents** with different specializations work together to accomplish complex tasks that a single agent cannot handle efficiently.

### Real-World Analogy
Think of a **hospital**:
```
┌─────────────────────────────────────────────────────────┐
│                    HOSPITAL (System)                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Patient arrives with symptoms                          │
│            │                                             │
│            ▼                                             │
│   ┌─────────────────┐                                   │
│   │   Receptionist   │  ← Intake Agent                  │
│   │   (Triage)       │                                   │
│   └────────┬────────┘                                   │
│            │                                             │
│   ┌────────┴────────┬─────────────┐                     │
│   ▼                 ▼             ▼                     │
│ ┌──────┐      ┌──────────┐  ┌──────────┐               │
│ │Doctor│      │ Lab Tech │  │ Pharmacist│               │
│ │Agent │      │  Agent   │  │   Agent   │               │
│ └──────┘      └──────────┘  └──────────┘               │
│                                                          │
│   Each specialist has:                                   │
│   - Specific expertise                                   │
│   - Own tools (stethoscope, lab equipment, medicines)   │
│   - Communicates with others                            │
│   - Shares patient records (shared memory)              │
└─────────────────────────────────────────────────────────┘
```

### Why Multi-Agent?

| Single Agent | Multi-Agent |
|--------------|-------------|
| One prompt does everything | Specialized prompts for each task |
| Gets confused with complex tasks | Each agent focuses on one thing |
| Context window limits | Distributed context |
| No collaboration | Agents can verify each other's work |
| Hard to debug | Clear responsibility per agent |

---

## 2. Single Agent vs Multi-Agent

### Single Agent Approach
```python
# One agent tries to do everything
response = llm.invoke("""
    You are a recruiter. Given these resumes and this job description:
    1. Parse all resumes
    2. Match skills
    3. Rank candidates
    4. Schedule interviews
    5. Generate assessment questions

    Do ALL of this in one response.
""")
# Problem: Too complex, prone to errors, hard to maintain
```

### Multi-Agent Approach
```python
# Each agent does ONE thing well
resume_parser = Agent(role="Resume Parser", goal="Extract structured data")
skill_matcher = Agent(role="Skill Matcher", goal="Match skills semantically")
scheduler = Agent(role="Scheduler", goal="Coordinate interviews")

# They work together, each doing their specialty
```

### When to Use Multi-Agent?

| Use Multi-Agent When | Stick to Single Agent When |
|---------------------|---------------------------|
| Task has 3+ distinct subtasks | Simple Q&A |
| Different expertise needed | Single-domain task |
| Need verification/voting | Quick response needed |
| Complex workflows | Low complexity |
| Parallel processing possible | Sequential simple steps |

---

## 3. Core Concepts

### 3.1 Agent
An autonomous unit with:
```python
Agent = {
    "role": "What it does",           # e.g., "Resume Screener"
    "goal": "What it aims to achieve", # e.g., "Find qualified candidates"
    "backstory": "Context/expertise",  # e.g., "15 years recruiting experience"
    "tools": [...],                    # Functions it can call
    "llm": "model to use",             # e.g., "claude-3-sonnet"
    "memory": True/False,              # Remember past interactions
}
```

### 3.2 Task
A specific job for an agent:
```python
Task = {
    "description": "What to do",
    "agent": agent_to_execute,
    "expected_output": "What format/content",
    "context": [other_tasks],  # Dependencies
    "tools": [...],            # Specific tools for this task
}
```

### 3.3 Crew/Team
A group of agents working together:
```python
Crew = {
    "agents": [agent1, agent2, agent3],
    "tasks": [task1, task2, task3],
    "process": "sequential" | "hierarchical" | "parallel",
    "memory": shared_memory,
}
```

### 3.4 Tools
Functions agents can call:
```python
@tool
def parse_resume(file_path: str) -> dict:
    """Extract data from resume file"""
    # Implementation
    return structured_data

@tool
def search_linkedin(name: str) -> dict:
    """Search LinkedIn for candidate info"""
    # Implementation
    return profile_data
```

### 3.5 Shared Memory
How agents share information:
```python
shared_memory = {
    "job_requirements": {...},
    "candidates": [...],
    "screening_results": [...],
    "decisions": [...],
}
# All agents can read/write to this
```

---

## 4. Orchestration Patterns

### Pattern 1: Sequential (Pipeline)
```
Agent A → Agent B → Agent C → Result
   │         │         │
   └─────────┴─────────┴── Each agent's output feeds the next
```

**When to use:** Tasks that depend on previous results

**Example - Resume Pipeline:**
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Parser     │ → │   Screener   │ → │   Ranker     │
│   Agent      │    │   Agent      │    │   Agent      │
└──────────────┘    └──────────────┘    └──────────────┘
     │                    │                    │
  Raw Resume →      Structured Data →    Ranked List
```

**Code:**
```python
from crewai import Crew, Process

crew = Crew(
    agents=[parser, screener, ranker],
    tasks=[parse_task, screen_task, rank_task],
    process=Process.sequential  # ← One after another
)
```

---

### Pattern 2: Hierarchical (Manager-Worker)
```
           ┌─────────────────┐
           │    Manager      │  ← Delegates & coordinates
           │     Agent       │
           └────────┬────────┘
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
   ┌───────┐   ┌───────┐   ┌───────┐
   │Worker │   │Worker │   │Worker │  ← Specialized workers
   │   A   │   │   B   │   │   C   │
   └───────┘   └───────┘   └───────┘
```

**When to use:** Complex tasks needing coordination, dynamic delegation

**Example - Recruitment Manager:**
```python
manager = Agent(
    role="Recruitment Manager",
    goal="Coordinate hiring process efficiently",
    allow_delegation=True  # Can assign tasks to others
)

crew = Crew(
    agents=[manager, parser, screener, scheduler],
    tasks=[hire_task],
    process=Process.hierarchical,  # ← Manager decides flow
    manager_agent=manager
)
```

---

### Pattern 3: Parallel (Concurrent)
```
              ┌───────────────┐
              │   Splitter    │
              └───────┬───────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
   ┌───────┐     ┌───────┐     ┌───────┐
   │Agent A│     │Agent B│     │Agent C│  ← Run simultaneously
   └───┬───┘     └───┬───┘     └───┬───┘
       │              │              │
       └──────────────┼──────────────┘
                      │
              ┌───────▼───────┐
              │   Aggregator  │
              └───────────────┘
```

**When to use:** Independent tasks, speed matters

**Example - Review Multiple Resumes:**
```python
# Each agent reviews different resumes at same time
async def parallel_review(resumes):
    tasks = [
        agent.review(resume)
        for resume in resumes
    ]
    results = await asyncio.gather(*tasks)
    return aggregate(results)
```

---

### Pattern 4: Consensus (Voting)
```
              ┌─────────────┐
              │  Candidate  │
              └──────┬──────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
   ┌───────┐    ┌───────┐    ┌───────┐
   │ Judge │    │ Judge │    │ Judge │
   │   1   │    │   2   │    │   3   │
   └───┬───┘    └───┬───┘    └───┬───┘
       │             │             │
       │  Score: 85  │  Score: 90  │  Score: 88
       │             │             │
       └─────────────┼─────────────┘
                     │
              ┌──────▼──────┐
              │   Average   │  → Final: 87.6
              │    Vote     │
              └─────────────┘
```

**When to use:** Important decisions, reducing bias

**Code:**
```python
def consensus_evaluation(candidate):
    scores = {
        "technical": technical_agent.evaluate(candidate),
        "cultural": culture_agent.evaluate(candidate),
        "experience": experience_agent.evaluate(candidate),
    }
    weights = {"technical": 0.4, "cultural": 0.3, "experience": 0.3}
    return weighted_average(scores, weights)
```

---

### Pattern 5: Supervisor (Router)
```
                 ┌─────────────┐
                 │  Supervisor │  ← Decides which agent to call
                 │   (Router)  │
                 └──────┬──────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │Technical │  │Behavioral│  │ Schedule │
    │  Agent   │  │  Agent   │  │  Agent   │
    └──────────┘  └──────────┘  └──────────┘
```

**When to use:** Dynamic routing based on input type

**Code (LangGraph style):**
```python
def supervisor(state):
    """Route to appropriate agent based on task type"""
    if state["task_type"] == "technical":
        return "technical_agent"
    elif state["task_type"] == "scheduling":
        return "scheduler_agent"
    else:
        return "general_agent"
```

---

### Pattern 6: Reflection (Self-Improvement)
```
┌─────────────────────────────────────────┐
│                                          │
│    ┌──────────┐     ┌──────────┐        │
│    │ Generator│ → │  Critic  │        │
│    │  Agent   │     │  Agent   │        │
│    └────┬─────┘     └────┬─────┘        │
│         │                │               │
│         │   Feedback     │               │
│         └────────────────┘               │
│                                          │
│    Loop until quality threshold met      │
└─────────────────────────────────────────┘
```

**When to use:** Quality-critical outputs

**Example:**
```python
def reflection_loop(task, max_iterations=3):
    for i in range(max_iterations):
        result = generator.execute(task)
        feedback = critic.review(result)

        if feedback.score > 0.9:
            return result

        task = f"{task}\n\nPrevious attempt feedback: {feedback}"

    return result
```

---

## 5. Popular Frameworks Comparison

### Framework Overview

| Framework | Creator | Best For | Complexity | Learning Curve |
|-----------|---------|----------|------------|----------------|
| **CrewAI** | João Moura | Role-based agents | Medium | Easy |
| **LangGraph** | LangChain | Graph workflows | High | Medium |
| **AutoGen** | Microsoft | Conversations | Medium | Medium |
| **Swarm** | OpenAI | Lightweight agents | Low | Easy |
| **Agency Swarm** | VRSEN | Complex hierarchies | High | Hard |

---

### CrewAI (Recommended for Beginners)

**Philosophy:** Agents are like team members with roles

```python
from crewai import Agent, Task, Crew, Process

# Define agents with clear roles
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive information",
    backstory="You have 10 years of research experience",
    tools=[search_tool, web_scraper],
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging content",
    backstory="Award-winning journalist",
    tools=[write_tool],
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the topic: {topic}",
    agent=researcher,
    expected_output="Detailed research report"
)

write_task = Task(
    description="Write article based on research",
    agent=writer,
    expected_output="Published-ready article",
    context=[research_task]  # Depends on research
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

# Execute
result = crew.kickoff(inputs={"topic": "AI in Healthcare"})
```

**Pros:**
- Easy to understand (role-based)
- Built-in process types
- Good documentation
- Active community

**Cons:**
- Less flexible than LangGraph
- Limited custom workflows

---

### LangGraph (Most Flexible)

**Philosophy:** Everything is a graph with nodes and edges

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# Define state
class AgentState(TypedDict):
    messages: list
    next_agent: str

# Define nodes (agents)
def parser_node(state):
    # Parse resume logic
    return {"messages": state["messages"] + ["Parsed resume"]}

def screener_node(state):
    # Screen candidate logic
    return {"messages": state["messages"] + ["Screened candidate"]}

def router(state):
    # Decide next step
    if "parsed" in state["messages"][-1]:
        return "screener"
    return END

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("parser", parser_node)
workflow.add_node("screener", screener_node)

workflow.add_edge("parser", router)  # Conditional edge
workflow.add_edge("screener", END)

workflow.set_entry_point("parser")

# Compile and run
app = workflow.compile()
result = app.invoke({"messages": [], "next_agent": "parser"})
```

**Pros:**
- Maximum flexibility
- Visual graph representation
- Stateful conversations
- Cycles and loops supported

**Cons:**
- Steeper learning curve
- More boilerplate code

---

### AutoGen (Microsoft)

**Philosophy:** Agents as conversational participants

```python
from autogen import AssistantAgent, UserProxyAgent

# Create agents
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "coding"}
)

# Agents chat to solve problems
user_proxy.initiate_chat(
    assistant,
    message="Write a Python function to parse resumes"
)
```

**Pros:**
- Natural conversation flow
- Code execution built-in
- Good for coding tasks

**Cons:**
- Less structured workflows
- Can be chatty/verbose

---

### OpenAI Swarm (Simplest)

**Philosophy:** Minimal, lightweight agent handoffs

```python
from swarm import Swarm, Agent

client = Swarm()

# Simple agents
parser = Agent(
    name="Parser",
    instructions="You parse resumes into structured data"
)

screener = Agent(
    name="Screener",
    instructions="You evaluate candidates against requirements"
)

# Handoff function
def transfer_to_screener():
    return screener

parser.functions = [transfer_to_screener]

# Run
response = client.run(
    agent=parser,
    messages=[{"role": "user", "content": "Parse this resume..."}]
)
```

**Pros:**
- Extremely simple
- Lightweight
- Easy handoffs

**Cons:**
- Limited features
- No built-in memory
- Basic orchestration

---

## 6. Tools & Libraries

### Core Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| `crewai` | Multi-agent framework | `pip install crewai` |
| `langgraph` | Graph-based workflows | `pip install langgraph` |
| `langchain` | LLM utilities | `pip install langchain` |
| `anthropic` | Claude API | `pip install anthropic` |
| `openai` | OpenAI API | `pip install openai` |

### Document Processing

| Library | Purpose | Install |
|---------|---------|---------|
| `pymupdf` | PDF parsing | `pip install pymupdf` |
| `python-docx` | DOCX parsing | `pip install python-docx` |
| `unstructured` | Universal parser | `pip install unstructured` |

### Embeddings & Vector Search

| Library | Purpose | Install |
|---------|---------|---------|
| `sentence-transformers` | Text embeddings | `pip install sentence-transformers` |
| `chromadb` | Local vector DB | `pip install chromadb` |
| `pinecone-client` | Cloud vector DB | `pip install pinecone-client` |

### Integrations

| Library | Purpose | Install |
|---------|---------|---------|
| `google-api-python-client` | Google Calendar | `pip install google-api-python-client` |
| `resend` | Email sending | `pip install resend` |
| `fastapi` | API backend | `pip install fastapi` |

---

## 7. How Agents Communicate

### Method 1: Task Context (CrewAI)
```python
# Task output automatically passed to next task
task1 = Task(description="Parse resume", agent=parser)
task2 = Task(
    description="Screen candidate",
    agent=screener,
    context=[task1]  # ← Gets task1's output
)
```

### Method 2: Shared State (LangGraph)
```python
class SharedState(TypedDict):
    candidates: list
    screening_results: list

# All nodes read/write to same state
def parser(state):
    state["candidates"].append(parsed_data)
    return state

def screener(state):
    for candidate in state["candidates"]:
        state["screening_results"].append(screen(candidate))
    return state
```

### Method 3: Message Passing
```python
# Agents send messages to each other
class Message:
    sender: str
    receiver: str
    content: dict

message_queue = []

def send_message(sender, receiver, content):
    message_queue.append(Message(sender, receiver, content))

def receive_messages(agent_name):
    return [m for m in message_queue if m.receiver == agent_name]
```

### Method 4: Shared Memory Store
```python
import redis

# Redis as shared memory
redis_client = redis.Redis()

# Agent 1 writes
redis_client.set("candidate_123", json.dumps(candidate_data))

# Agent 2 reads
candidate = json.loads(redis_client.get("candidate_123"))
```

---

## 8. Building Blocks

### Block 1: Define Your Agents
```python
agents = {
    "jd_optimizer": {
        "role": "Job Description Specialist",
        "goal": "Create inclusive, clear job descriptions",
        "tools": ["analyze_bias", "suggest_keywords"]
    },
    "resume_parser": {
        "role": "Resume Parser",
        "goal": "Extract structured data from resumes",
        "tools": ["parse_pdf", "parse_docx", "extract_skills"]
    },
    "skill_matcher": {
        "role": "Skill Matching Expert",
        "goal": "Match candidate skills to requirements",
        "tools": ["semantic_match", "check_github"]
    },
    "scheduler": {
        "role": "Interview Coordinator",
        "goal": "Schedule interviews efficiently",
        "tools": ["check_calendar", "send_invite", "send_email"]
    },
    "assessor": {
        "role": "Assessment Designer",
        "goal": "Create relevant interview questions",
        "tools": ["generate_questions", "create_coding_challenge"]
    }
}
```

### Block 2: Define Your Workflow
```
JOB POSTING FLOW:
  Input: Raw JD
    │
    ▼
  ┌─────────────────┐
  │  JD Optimizer   │ → Improved JD (bias-free)
  └─────────────────┘
    │
    ▼
  Output: Optimized JD

CANDIDATE SCREENING FLOW:
  Input: Resumes + JD
    │
    ▼
  ┌─────────────────┐
  │  Resume Parser  │ → Structured candidate data
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Skill Matcher  │ → Ranked candidates with scores
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │   Scheduler     │ → Interview invites sent
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │    Assessor     │ → Custom interview questions
  └─────────────────┘
    │
    ▼
  Output: Complete hiring package
```

### Block 3: Define Tools
```python
# Tool 1: Parse Resume
@tool
def parse_resume(file_path: str) -> dict:
    """Extract structured data from PDF/DOCX resume"""
    pass

# Tool 2: Match Skills
@tool
def semantic_skill_match(
    candidate_skills: list,
    required_skills: list
) -> dict:
    """Calculate semantic similarity between skills"""
    pass

# Tool 3: Check Calendar
@tool
def check_availability(
    email: str,
    date_range: tuple
) -> list:
    """Get available time slots from Google Calendar"""
    pass

# Tool 4: Send Email
@tool
def send_interview_invite(
    candidate_email: str,
    interviewer_email: str,
    datetime: str
) -> bool:
    """Send calendar invite and email notification"""
    pass
```

### Block 4: Define State/Memory
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RecruitmentState:
    # Input
    job_description: str
    resumes: List[str]  # file paths

    # Processed
    optimized_jd: str = ""
    candidates: List[Dict] = None
    skill_matches: List[Dict] = None

    # Output
    ranked_candidates: List[Dict] = None
    scheduled_interviews: List[Dict] = None
    assessment_questions: List[Dict] = None

    # Metadata
    current_step: str = "start"
    errors: List[str] = None
```

---

## 9. Recommended Approach for Our Project

### Why CrewAI?

| Reason | Explanation |
|--------|-------------|
| **Beginner Friendly** | Role-based agents are intuitive |
| **Built-in Patterns** | Sequential, hierarchical processes included |
| **Good Documentation** | Easy to learn |
| **Production Ready** | Used in real applications |
| **Flexible** | Can customize as needed |

### Our Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SMART RECRUITER                          │
│                   CrewAI Multi-Agent System                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 ORCHESTRATOR CREW                       │ │
│  │               (Process: Hierarchical)                   │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│      ┌────────────────────┼────────────────────┐            │
│      │                    │                    │            │
│      ▼                    ▼                    ▼            │
│  ┌────────┐         ┌──────────┐        ┌──────────┐       │
│  │  JD    │         │ SCREENING│        │INTERVIEW │       │
│  │ CREW   │         │   CREW   │        │   CREW   │       │
│  └────────┘         └──────────┘        └──────────┘       │
│  Sequential          Sequential          Sequential         │
│                                                              │
│  Agents:             Agents:             Agents:            │
│  - JD Optimizer      - Parser            - Scheduler        │
│                      - Skill Matcher     - Assessor         │
│                      - Ranker                               │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Decision

We'll use a **Hybrid Approach**:

1. **Top Level:** Hierarchical (Manager delegates to crews)
2. **Within Crews:** Sequential (Pipeline processing)
3. **Evaluation:** Consensus (Multiple agents vote on candidates)

---

## 10. Implementation Plan

### Phase 1: Foundation (Setup)
```
□ Create project structure
□ Install dependencies
□ Set up configuration
□ Create base agent class
□ Create tool decorators
```

### Phase 2: Tools Development
```
□ Resume parser (PDF, DOCX)
□ Skill extractor
□ Semantic matcher
□ Calendar integration
□ Email service
```

### Phase 3: Individual Agents
```
□ JD Optimizer Agent
□ Resume Parser Agent
□ Skill Matcher Agent
□ Scheduler Agent
□ Assessment Agent
```

### Phase 4: Crews Setup
```
□ JD Optimization Crew
□ Screening Crew
□ Interview Crew
□ Master Orchestrator
```

### Phase 5: Integration
```
□ Connect all crews
□ Shared state management
□ Error handling
□ Logging
```

### Phase 6: API & Dashboard
```
□ FastAPI backend
□ REST endpoints
□ Simple frontend (optional)
```

### Phase 7: Testing & Polish
```
□ Unit tests
□ Integration tests
□ Documentation
□ README
```

---

## Quick Start Code

Here's a minimal example to get started:

```python
# minimal_example.py
from crewai import Agent, Task, Crew, Process

# 1. Create an agent
resume_analyzer = Agent(
    role="Resume Analyst",
    goal="Analyze resumes and extract key information",
    backstory="Expert HR analyst with 10 years experience",
    verbose=True
)

# 2. Create a task
analyze_task = Task(
    description="""
    Analyze this resume and extract:
    - Name
    - Skills
    - Years of experience
    - Education

    Resume: {resume_text}
    """,
    agent=resume_analyzer,
    expected_output="Structured candidate profile"
)

# 3. Create a crew
crew = Crew(
    agents=[resume_analyzer],
    tasks=[analyze_task],
    process=Process.sequential,
    verbose=True
)

# 4. Run
result = crew.kickoff(inputs={
    "resume_text": "John Doe, Software Engineer, 5 years Python..."
})

print(result)
```

---

## Summary

| Concept | What We'll Use |
|---------|---------------|
| Framework | CrewAI |
| Pattern | Hierarchical + Sequential |
| Agents | 5 specialized agents |
| Tools | Custom Python functions |
| State | Dataclass + Redis |
| Communication | Task context + shared state |

---

Ready to build? Let's start with Phase 1!
