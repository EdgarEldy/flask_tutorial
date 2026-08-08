from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar

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
