from tests.test_artifact import artifact
from src.replay import ReplayEngine
from src.logger import save_run_log


print("\n--- STARTING REPLAY TEST ---")

engine = ReplayEngine()


# ---------------------------------
# Test 1: Successful member lookup
# ---------------------------------

print("\n--- SUCCESS TEST ---")

success_result = engine.execute(
    artifact,
    {
        "member_id": "12345"
    },
)

print(success_result)

save_run_log(
    "replay_success.json",
    {
        "capability": artifact.name,
        "input": {
            "member_id": "[REDACTED]"
        },
        "result": success_result,
    },
)


# ---------------------------------
# Test 2: Member not found
# ---------------------------------

print("\n--- MEMBER NOT FOUND TEST ---")

not_found_result = engine.execute(
    artifact,
    {
        "member_id": "99999"
    },
)

print(not_found_result)

save_run_log(
    "replay_not_found.json",
    {
        "capability": artifact.name,
        "input": {
            "member_id": "[REDACTED]"
        },
        "result": not_found_result,
    },
)


print("\n--- REPLAY TEST COMPLETE ---")