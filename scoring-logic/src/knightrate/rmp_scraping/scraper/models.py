from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class Rating(BaseModel):
    """Represents a single student rating for a professor on RateMyProfessors."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    prof_id: str = ""
    attendance_mandatory: Optional[str] = Field(alias="attendanceMandatory", default=None)
    clarity_rating: float = Field(alias="clarityRating")
    course_class: Optional[str] = Field(alias="class", default=None)
    comment: str
    date: str
    difficulty_rating: float = Field(alias="difficultyRating")
    grade: Optional[str] = None
    helpful_rating: float = Field(alias="helpfulRating")
    is_for_credit: Optional[bool] = Field(alias="isForCredit", default=None)
    is_for_online_class: Optional[bool] = Field(alias="isForOnlineClass", default=None)
    rating_tags: List[str] = Field(alias="ratingTags", default_factory=list)
    teacher_note: Any = Field(alias="teacherNote", default=None)
    textbook_use: Optional[int] = Field(alias="textbookUse", default=None)
    thumbs: List[Any] = Field(default_factory=list)
    thumbs_down_total: int = Field(alias="thumbsDownTotal", default=0)
    thumbs_up_total: int = Field(alias="thumbsUpTotal", default=0)
    would_take_again: Optional[int] = Field(alias="wouldTakeAgain", default=None)


class Professor(BaseModel):
    """Represents a professor scraped from RateMyProfessors, including their reviews."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    department: Optional[str] = None
    num_ratings: int = Field(alias="numRatings", default=0)
    avg_difficulty: float = Field(alias="avgDifficulty", default=0.0)
    avg_rating: float = Field(alias="avgRating", default=0.0)
    would_take_again_percent: Optional[float] = Field(alias="wouldTakeAgainPercent", default=None)
    all_reviews_scraped: bool = Field(alias="allReviewsScraped", default=False)
    reviews: List[Rating] = Field(default_factory=list)
