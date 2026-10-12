from src.discovery import (
    DiscoveryAgent,
    save_discovery_log,
)


goal = (
    "Look up member 12345 and read "
    "their current savings balance."
)


print(
    "\n--- STARTING GEMINI DISCOVERY ---"
)


agent = DiscoveryAgent()


result = agent.run(
    goal=goal,
    url="http://127.0.0.1:5000",
)


print(
    "\n--- DISCOVERY RESULT ---"
)


print(result)


save_discovery_log(
    result
)


print(
    "\nDiscovery evidence saved."
)