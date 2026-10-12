from typing import Any, Dict

from src.artifact import CapabilityArtifact
from src.policy import validate_url, validate_action
from src.surface import BrowserSurface


class ReplayEngine:
    def execute(
        self,
        artifact: CapabilityArtifact,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:

        surface = BrowserSurface()

        try:
            # Safety: verify target URL is allowed
            validate_url(artifact.start_url, artifact)

            # Start browser
            surface.start()
            surface.navigate(artifact.start_url)

            # Execute artifact steps
            for step in artifact.steps:
                validate_action(step.action, artifact)

                value = step.value

                # Replace {{member_id}} with actual input
                if value:
                    for key, input_value in inputs.items():
                        value = value.replace(
                            "{{" + key + "}}",
                            str(input_value),
                        )

                # TYPE action
                if step.action.value == "type":
                    if (
                        step.locator
                        and step.locator.strategy == "label"
                    ):
                        surface.type_by_label(
                            step.locator.value,
                            value,
                        )

                # CLICK action
                elif step.action.value == "click":
                    if (
                        step.locator
                        and step.locator.strategy == "role"
                    ):
                        surface.click_by_role(
                            step.locator.role,
                            step.locator.value,
                        )

            # Check for business/application messages
            alert = surface.page.locator('[role="alert"]')

            if alert.count() > 0:
                message = alert.inner_text().strip()

                # Expected business outcome
                if "Member not found" in message:
                    surface.screenshot(
                        "evidence/replay_not_found.png"
                    )

                    return {
                        "status": "BUSINESS_OUTCOME",
                        "outcome": "MEMBER_NOT_FOUND",
                        "message": message,
                    }

                # Unexpected application error
                surface.screenshot(
                    "evidence/replay_failure.png"
                )

                return {
                    "status": "FAILURE",
                    "error_type": "APPLICATION_ERROR",
                    "message": message,
                }

            # Verify success checkpoint
            checkpoint_locator = (
                artifact.success_checkpoint.locator
            )

            if checkpoint_locator.strategy != "css":
                return {
                    "status": "FAILURE",
                    "error_type": "UNSUPPORTED_CHECKPOINT",
                    "message": "Unsupported checkpoint locator strategy.",
                }

            checkpoint = surface.page.locator(
                checkpoint_locator.value
            )

            if checkpoint.count() == 0:
                surface.screenshot(
                    "evidence/replay_failure.png"
                )

                return {
                    "status": "FAILURE",
                    "error_type": "CHECKPOINT_FAILED",
                    "message": "Success checkpoint was not found.",
                }

            checkpoint_text = checkpoint.inner_text().strip()

            if (
                artifact.success_checkpoint.expected
                not in checkpoint_text
            ):
                surface.screenshot(
                    "evidence/replay_failure.png"
                )

                return {
                    "status": "FAILURE",
                    "error_type": "CHECKPOINT_MISMATCH",
                    "message": (
                        f"Expected "
                        f"'{artifact.success_checkpoint.expected}' "
                        f"but observed '{checkpoint_text}'."
                    ),
                }

            # Extract outputs
            outputs = {}

            for output in artifact.outputs:
                if output.locator.strategy == "css":
                    outputs[output.name] = surface.read_css(
                        output.locator.value
                    )

            # Save evidence
            surface.screenshot(
                "evidence/replay_success.png"
            )

            return {
                "status": "SUCCESS",
                "outputs": outputs,
            }

        except Exception as error:
            try:
                if surface.page:
                    surface.screenshot(
                        "evidence/replay_failure.png"
                    )
            except Exception:
                pass

            return {
                "status": "FAILURE",
                "error_type": type(error).__name__,
                "message": str(error),
            }

        finally:
            surface.close()