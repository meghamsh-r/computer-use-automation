from pathlib import Path

from src.artifact import (
    CapabilityArtifact,
    Parameter,
    Output,
    Step,
    Locator,
    Checkpoint,
    ActionType,
)


# Define the reusable capability artifact
artifact = CapabilityArtifact(
    name="lookup_member_balance",
    description="Look up a member and return their savings balance.",
    target_app="Demo Member Servicing Portal",
    start_url="http://127.0.0.1:5000",

    inputs=[
        Parameter(
            name="member_id",
            type="string",
            description="Member ID to search for",
        )
    ],

    outputs=[
        Output(
            name="savings_balance",
            type="string",
            description="Current savings balance",
            locator=Locator(
                strategy="css",
                value="#savings-balance",
            ),
        )
    ],

    steps=[
        Step(
            id="step_1",
            action=ActionType.TYPE,
            locator=Locator(
                strategy="label",
                value="Member ID",
            ),
            value="{{member_id}}",
            description="Enter the member ID",
            expected_state="Member ID is entered in the search field.",
        ),

        Step(
            id="step_2",
            action=ActionType.CLICK,
            locator=Locator(
                strategy="role",
                role="button",
                value="Search Member",
            ),
            description="Search for the member.",
            expected_state="Member details or a business outcome is displayed.",
        ),
    ],

    success_checkpoint=Checkpoint(
        description="Member record successfully loaded.",
        locator=Locator(
            strategy="css",
            value="#lookup-success",
        ),
        expected="Member record loaded successfully.",
    ),

    allowed_domains=[
        "127.0.0.1"
    ],

    allowed_actions=[
        ActionType.TYPE,
        ActionType.CLICK,
        ActionType.READ,
    ],

    metadata={
        "surface": "web",
        "artifact_status": "draft",
        "contains_sensitive_data": False,
    },
)


# Print artifact so we can inspect it
print("\n--- CAPABILITY ARTIFACT ---\n")
print(artifact.model_dump_json(indent=2))


# Save artifact as assessment evidence
evidence_directory = Path("evidence")
evidence_directory.mkdir(exist_ok=True)

artifact_path = evidence_directory / "example_artifact.json"

with open(
    artifact_path,
    "w",
    encoding="utf-8",
) as file:
    file.write(
        artifact.model_dump_json(indent=2)
    )


print(
    f"\nArtifact saved to: {artifact_path}"
)