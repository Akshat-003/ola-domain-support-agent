from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class TicketData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    status: str
    resolution_time_hours: float
    escalation_score: float = Field(ge=0, le=1)
    escalation_priority: Literal["High", "Normal"]


class TicketLookupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["ticket_lookup"]
    data: TicketData


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["knowledge_base"]
    answer: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["error"]
    message: str


SupportResponse = Union[
    TicketLookupResponse,
    KnowledgeBaseResponse,
    ErrorResponse
]


def validate_support_response(response):
    models = [
        TicketLookupResponse,
        KnowledgeBaseResponse,
        ErrorResponse
    ]

    validation_errors = []

    for model in models:
        try:
            validated = model.model_validate(response)
            return validated.model_dump()

        except Exception as error:
            validation_errors.append(str(error))

    print("Schema validation details:")
    for error in validation_errors:
        print(error)

    raise ValueError("Invalid support agent response schema.")
