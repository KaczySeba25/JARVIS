import asyncio
from jarvis_core import JarvisCore

async def main():
    jarvis = JarvisCore(confirm=lambda prompt: input(f"\n{prompt} [t/N]: ").strip().lower() in {"t", "tak", "y", "yes"})
    print("Jarvis gotowy. Wpisz 'exit', aby zakoÅ„czyÄ‡.")
    while True:
        message = input("\nTy: ").strip()
        if message.lower() in {"exit", "quit", "wyjdz", "wyjdÅº"}: break
        if message: print("\nJarvis:", jarvis.ask(message))

if __name__ == "__main__":
    asyncio.run(main())


