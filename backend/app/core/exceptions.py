import logging
from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class HRMSException(Exception):
    """Base exception for all domain exceptions in HRMS."""
    def __init__(
        self,
        message: str,
        error_code: str = "HRMS_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(HRMSException):
    def __init__(self, resource: str, identifier: Any = None):
        msg = f"{resource} not found" if identifier is None else f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=msg,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedException(HRMSException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UnauthorizedException(HRMSException):
    def __init__(self, message: str = "Authentication credentials were not provided or are invalid"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class DuplicateResourceException(HRMSException):
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists.",
            error_code="DUPLICATE_RESOURCE",
            status_code=status.HTTP_409_CONFLICT,
        )


class BusinessRuleException(HRMSException):
    def __init__(self, message: str, error_code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized error handlers to format responses consistently."""

    @app.exception_handler(HRMSException)
    async def hrms_exception_handler(request: Request, exc: HRMSException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Default error code based on status code
        error_code_map = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            500: "INTERNAL_SERVER_ERROR",
        }
        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
        detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": error_code,
                "message": detail_msg,
                "details": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for error in exc.errors():
            loc = " -> ".join(str(l) for l in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            formatted_errors.append({"field": loc, "issue": msg, "type": error.get("type")})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the provided fields.",
                "details": formatted_errors,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error(f"Database IntegrityError: {str(exc.orig)}")
        # Safe message without leaking internal schema details
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error_code": "DATABASE_INTEGRITY_ERROR",
                "message": "Database constraint violation. A record with duplicate unique fields or an invalid foreign key reference was detected.",
                "details": None,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "DATABASE_ERROR",
                "message": "A database error occurred while processing the request.",
                "details": None,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception occurred: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred on the server.",
                "details": None,
            },
        )
