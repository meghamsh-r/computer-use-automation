from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    READ = "read"
    WAIT = "wait"


class Locator(BaseModel):
    strategy: Literal["role", "label", "text", "css"]
    value: str
    role: Optional[str] = None


class Parameter(BaseModel):
    name: str
    type: Literal["string", "integer", "boolean"]
    description: str
    required: bool = True


class Output(BaseModel):
    name: str
    type: Literal["string", "integer", "boolean"]
    description: str
    locator: Locator


class Step(BaseModel):
    id: str
    action: ActionType
    locator: Optional[Locator] = None

    # Literal value or template such as "{{member_id}}"
    value: Optional[str] = None

    description: str
    expected_state: Optional[str] = None


class Checkpoint(BaseModel):
    description: str
    locator: Locator
    expected: str


class CapabilityArtifact(BaseModel):
    schema_version: str = "1.0"
    capability_version: str = "1.0"

    name: str
    description: str

    target_app: str
    start_url: str

    inputs: List[Parameter]
    outputs: List[Output]

    steps: List[Step]

    success_checkpoint: Checkpoint

    allowed_domains: List[str]
    allowed_actions: List[ActionType]

    metadata: Dict[str, Any] = Field(default_factory=dict)