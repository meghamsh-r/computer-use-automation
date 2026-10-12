from src.surface import BrowserSurface
from src.handoff import HandoffManager


surface = BrowserSurface()
handoff = HandoffManager()

try:
    surface.start()

    surface.navigate(
        "http://127.0.0.1:5000"
    )

    print("\nAutomation currently controls the session.")

    # Simulate a condition automation cannot safely resolve.
    handoff.request_human(
        reason=(
            "Automation encountered a condition "
            "requiring operator review."
        ),
        surface=surface,
    )

    handoff.wait_for_human()

    # IMPORTANT:
    # This is still the SAME browser/page/session.
    current_url = surface.page.url

    print("\nAutomation resumed.")
    print("Current URL:", current_url)

    surface.screenshot(
        "evidence/handoff_resumed.png"
    )

    handoff.complete()
    handoff.save()

    print("\n--- HANDOFF TEST SUCCESSFUL ---")

finally:
    surface.close()