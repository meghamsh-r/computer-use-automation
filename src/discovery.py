import json
import os

from pathlib import Path

from dotenv import load_dotenv
from google import genai

from src.surface import BrowserSurface


load_dotenv()


class DiscoveryAgent:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY was not found. "
                "Add it to the .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def observe(
        self,
        surface: BrowserSurface,
    ) -> str:

        return (
            surface.page
            .locator("body")
            .inner_text()
        )

    def decide(
        self,
        goal: str,
        observation: str,
    ) -> dict:

        prompt = f"""
You are controlling a demo banking web application.

Your job is to accomplish the user's goal by choosing
ONE action at a time.

GOAL:
{goal}

CURRENT PAGE:
{observation}

Allowed actions:

1. type
Use this to type into an input.

Example:
{{"action":"type","target":"Member ID","value":"12345"}}

2. click
Use this to click a button.

Example:
{{"action":"click","target":"Search Member"}}

3. read
Use this when the requested information is visible.

Example:
{{"action":"read","target":"Savings Balance"}}

4. done
Use this only after the goal has been completed.

Example:
{{"action":"done","target":null}}

Return exactly one JSON object.
Do not return markdown.
Do not return an explanation.
"""

        response = (
            self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        )

        text = response.text.strip()

        # Defensive cleanup in case the model
        # surrounds JSON with markdown fences.
        if text.startswith("```"):
            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        return json.loads(text)

    def run(
        self,
        goal: str,
        url: str,
        max_steps: int = 8,
    ) -> dict:

        surface = BrowserSurface()

        history = []

        try:
            surface.start()

            surface.navigate(url)

            for step_number in range(
                1,
                max_steps + 1,
            ):

                observation = self.observe(
                    surface
                )

                decision = self.decide(
                    goal,
                    observation,
                )

                action = decision.get(
                    "action"
                )

                target = decision.get(
                    "target"
                )

                # Do not persist typed values such
                # as member IDs in discovery logs.
                history.append({
                    "step": step_number,
                    "action": action,
                    "target": target,
                })

                print(
                    f"Step {step_number}: "
                    f"{action} -> {target}"
                )

                if action == "type":

                    surface.type_by_label(
                        target,
                        decision.get(
                            "value",
                            ""
                        ),
                    )

                elif action == "click":

                    surface.click_by_role(
                        "button",
                        target,
                    )

                elif action == "read":

                    # Gemini receives the page
                    # observation again on the next
                    # iteration, so no UI mutation
                    # is necessary here.
                    pass

                elif action == "done":

                    surface.screenshot(
                        "evidence/"
                        "discovery_success.png"
                    )

                    return {
                        "status": "SUCCESS",
                        "steps": history,
                    }

                else:
                    surface.screenshot(
                        "evidence/"
                        "discovery_stuck.png"
                    )

                    return {
                        "status": "STUCK",
                        "reason":
                            "Model returned "
                            "an unsupported action.",
                        "steps": history,
                    }

            surface.screenshot(
                "evidence/discovery_stuck.png"
            )

            return {
                "status": "STUCK",
                "reason":
                    "Maximum steps reached.",
                "steps": history,
            }

        except Exception as error:

            try:
                if surface.page:
                    surface.screenshot(
                        "evidence/"
                        "discovery_failure.png"
                    )

            except Exception:
                pass

            return {
                "status": "FAILURE",
                "error_type":
                    type(error).__name__,
                "message":
                    str(error),
                "steps":
                    history,
            }

        finally:
            surface.close()


def save_discovery_log(
    result: dict,
):

    Path("evidence").mkdir(
        exist_ok=True
    )

    with open(
        "evidence/discovery_run.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
        )