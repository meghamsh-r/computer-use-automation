from urllib.parse import urlparse
from src.artifact import ActionType, CapabilityArtifact


class PolicyViolation(Exception):
    pass


def validate_url(url: str, artifact: CapabilityArtifact):
    domain = urlparse(url).hostname

    if domain not in artifact.allowed_domains:
        raise PolicyViolation(
            f"Domain '{domain}' is not allowed."
        )


def validate_action(
    action: ActionType,
    artifact: CapabilityArtifact
):
    if action not in artifact.allowed_actions:
        raise PolicyViolation(
            f"Action '{action.value}' is not allowed."
        )