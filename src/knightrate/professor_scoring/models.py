from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class Scores(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    raw_difficulty_score: float = Field(alias="rawDifficultyScore", default=0.0, exclude=True)
    rating_score: float = Field(alias="ratingScore", default=0.0, exclude=True)
    would_take_again_score: float | str = Field(alias="wouldTakeAgainScore", default="Unavailable")
    tag_friction_score: float = Field(alias="tagFrictionScore", default=0.0, exclude=True)
    tag_quality_score: float = Field(alias="tagQualityScore", default=0.0, exclude=True)
    difficulty: float = Field(alias="difficulty", default=0.0)
    quality: float = Field(alias="quality", default=0.0)
    overall: float = Field(alias="overall", default=0.0)
    archetype: str = Field(alias="archetype", default="Unknown")
    is_polarizing: bool = Field(alias="isPolarizing", default=False)
    top_three_tags: list[str] = Field(alias="topThreeTags", default_factory=list)
    time_last_taught: str = Field(alias="timeLastTaught", default="Unknown")

class Review(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    attendance_mandatory: Optional[str] = Field(alias="attendanceMandatory", default=None)
    clarity_rating: float = Field(alias="clarityRating")
    course_class: str = Field(alias="class", default="unknown")
    comment: str = ""
    date: str = ""
    difficulty_rating: float = Field(alias="difficultyRating")
    grade: Optional[str] = None
    helpful_rating: float = Field(alias="helpfulRating")
    is_for_credit: Optional[bool] = Field(alias="isForCredit", default=None)
    is_for_online_class: Optional[bool] = Field(alias="isForOnlineClass", default=None)
    rating_tags: List[str] = Field(alias="ratingTags", default_factory=list)
    teacher_note: Optional[Any] = Field(alias="teacherNote", default=None)
    textbook_use: Optional[int] = Field(alias="textbookUse", default=None)
    thumbs: List[Any] = Field(default_factory=list)
    thumbs_down_total: int = Field(alias="thumbsDownTotal", default=0)
    thumbs_up_total: int = Field(alias="thumbsUpTotal", default=0)
    would_take_again: Optional[int] = Field(alias="wouldTakeAgain", default=None)

class Professor(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = ""
    first_name: str = Field(alias="firstName", default="")
    last_name: str = Field(alias="lastName", default="")
    department: Optional[str] = None
    num_ratings: int = Field(alias="numRatings", default=0)
    avg_difficulty: float = Field(alias="avgDifficulty", default=0.0)
    avg_rating: float = Field(alias="avgRating", default=0.0)
    would_take_again_percent: float = Field(alias="wouldTakeAgainPercent", default=-1)
    all_reviews_scraped: bool = Field(alias="allReviewsScraped", default=False)
    reviews: List[Review] = Field(default_factory=list)
    
    # Unified Catalog fields
    role: Optional[str] = None
    field_of_study: Optional[str] = Field(alias="fieldOfStudy", default=None)
    date_joined_ucf: Optional[str] = Field(alias="dateJoinedUcf", default=None)
    level_of_education: Optional[str] = Field(alias="levelOfEducation", default=None)
    graduated_from: Optional[str] = Field(alias="graduatedFrom", default=None)
    is_emeritus: bool = Field(alias="isEmeritus", default=False)
    courses_taught: List[str] = Field(default_factory=list)
    
    # Engine output field
    scores: Optional[Scores] = None

class GlobalStatistics(BaseModel):
    model_config = ConfigDict(extra="allow")
    avg_difficulty: float = Field(alias="avgDifficulty", default=0.0)
    avg_quality: float = Field(alias="avgQuality", default=0.0)
    avg_overall: float = Field(alias="avgOverall", default=0.0)
    avg_would_take_again: float = Field(alias="avgWouldTakeAgain", default=0.0)
