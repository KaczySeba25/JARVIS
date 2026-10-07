import sys, json
sys.path.insert(0, r"C:\Jarvis\agent")
import jarvis_core
j = jarvis_core.JarvisCore(confirm=lambda p: False)
print("PROVIDER:", j.model_router.provider, "| MODEL:", j.model_router.model)
print("SKILLS:", len(j.skills()))
print("SKILL_BUILDER invalid ->", str(j.run_skill("skill_builder", "invalid"))[:200])
p = j.system_prompt()
print("PROMPT chars:", len(p))
print("HAS_RULES:", "[FORMAT ODPOWIEDZI]" in p, "| HAS_PERSONA:", p.startswith("Tożsamość: Jarvis"))
print("DECISION:", jarvis_core.JarvisCore._decision('Ok. {"type":"tool_call","name":"web_research","argument":"x"}'))
