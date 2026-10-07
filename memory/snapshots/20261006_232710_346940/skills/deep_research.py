"""Multi-source research with local, cited knowledge storage."""
try:
    from research_engine import deep_research
except ImportError:
    from agent.research_engine import deep_research

def run(topic: str):
    if not topic or len(topic.strip()) < 3:
        return "Podaj konkretny temat researchu."
    return deep_research(topic.strip())
