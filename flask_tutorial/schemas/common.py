from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar

from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Field, Integer, List, Nested, String

T = TypeVar("T")


@dataclass
class PageResponse(Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total_count: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return -(-self.total_count // self.page_size)

    def to_dict(self) -> dict:
        return {
            "items": self.items,
            "page": self.page,
            "page_size": self.page_size,
            "total_count": self.total_count,
            "total_pages": self.total_pages,
        }


@dataclass
class ApiResponse(Generic[T]):
    success: bool
    message: str
    data: T | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def ok(cls, data: T, message: str) -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str) -> "ApiResponse[None]":
        return cls(success=False, message=message, data=None)

    def to_dict(self) -> dict:
        data = self.data
        if hasattr(data, "to_dict"):
            data = data.to_dict()
        return {
            "success": self.success,
            "message": self.message,
            "data": data,
            "timestamp": self.timestamp.isoformat(),
        }


class ApiResponseSchema(Schema):
    """The marshmallow counterpart of ApiResponse, set as APIFlask's
    BASE_RESPONSE_SCHEMA so @app.output(SomeSchema) serializes SomeSchema
    under the "data" key while keeping this envelope around it, and
    documents the nested shape correctly in the OpenAPI spec.

    Views using @app.output should return the ApiResponse instance itself
    (e.g. `return ApiResponse.ok(category, "...")`), not `.to_dict()` -
    this schema dumps the real `timestamp` datetime, matching the ISO-8601
    format `ApiResponse.to_dict()` produces for the manual-jsonify path
    (error_handlers.py, /health). Calling `.to_dict()` first would hand
    this DateTime field an already-stringified value instead.
    """

    success = Boolean(required=True)
    message = String(required=True)
    data = Field()
    timestamp = DateTime(required=True)


def make_page_schema(item_schema: type[Schema], name: str) -> type[Schema]:
    """Builds a Schema class shaped like PageResponse.to_dict() (items,
    page, page_size, total_count, total_pages) for a given item schema,
    for use as the @app.output schema on paginated list endpoints."""
    return type(
        name,
        (Schema,),
        {
            "items": List(Nested(item_schema)),
            "page": Integer(),
            "page_size": Integer(),
            "total_count": Integer(),
            "total_pages": Integer(),
        },
    )
