"""Exceptions used by candidate and placement workflows."""


class PlacementSystemError(Exception):
    """Base class for expected application errors."""


class ValidationError(PlacementSystemError):
    """Raised when user-provided business data is invalid."""


class DuplicateCandidateError(PlacementSystemError):
    """Raised when a candidate email is already registered."""
