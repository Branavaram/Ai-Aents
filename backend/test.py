import os
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

print("Groq key loaded:", bool(groq_key))
print("Groq key starts with:", groq_key[:6] if groq_key else "NONE")

if not groq_key or "your_groq" in groq_key.lower():
    print("\nERROR: Please paste your real Groq key into the .env file!")
    exit(1)

# Point OpenAI client at Groq's OpenAI-compatible endpoint
os.environ["OPENAI_API_KEY"] = groq_key
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"

from crewai import Agent, Task, Crew, LLM

# Use Groq via OpenAI-compatible endpoint
groq_llm = LLM(
    model="openai/openai/gpt-oss-20b",
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1",
)

# Create a simple test agent
tester = Agent(
    role="Friendly Tester",
    goal="Confirm that CrewAI with Groq is set up correctly",
    backstory="You're a cheerful AI who confirms things are working.",
    llm=groq_llm,
    verbose=True,
)

# Give it a task
task = Task(
    description="Say hello and confirm CrewAI with Groq + Llama 3.3 is working. Keep it short and fun.",
    expected_output="A short friendly hello message.",
    agent=tester,
)

# Build the crew
crew = Crew(agents=[tester], tasks=[task], verbose=True)

# Run it!
result = crew.kickoff()

print("\n\n" + "="*50)
print("RESULT:")
print("="*50)
print(result)
