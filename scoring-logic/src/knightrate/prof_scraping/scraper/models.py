from pydantic import BaseModel


class ProfessorEntry(BaseModel):
    """Represents a single professor listing from the UCF Undergraduate Catalog."""
    raw: str
