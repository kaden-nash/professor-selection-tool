"""GraphQL query strings, operation names, and variable builders for RMP scraping."""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# Pagination constants
# ---------------------------------------------------------------------------

INITIAL_CURSOR = "YXJyYXljb25uZWN0aW9uOi0x"

_UCF_SCHOOL_ID = "U2Nob29sLTEwODI="
_PROFESSOR_PAGE_SIZE = 5
_REVIEW_PAGE_SIZE = 5

# ---------------------------------------------------------------------------
# Operation names
# ---------------------------------------------------------------------------

PROFESSOR_OPERATION = "TeacherSearchPaginationQuery"
RATINGS_OPERATION = "RatingsListQuery"

# ---------------------------------------------------------------------------
# Query strings
# ---------------------------------------------------------------------------

PROFESSOR_QUERY_STRING = (
    "query TeacherSearchPaginationQuery(\n  $count: Int!\n  $cursor: String\n"
    "  $query: TeacherSearchQuery!\n) {\n  search: newSearch {\n"
    "    teachers(query: $query, first: $count, after: $cursor) {\n"
    "      didFallback\n      edges {\n        cursor\n        node {\n"
    "          id\n          legacyId\n          avgRating\n          numRatings\n"
    "          wouldTakeAgainPercent\n          avgDifficulty\n          department\n"
    "          school {\n            name\n            id\n          }\n"
    "          firstName\n          lastName\n          isSaved\n          __typename\n"
    "        }\n      }\n      pageInfo {\n        hasNextPage\n        endCursor\n"
    "      }\n      resultCount\n      filters {\n        field\n        options {\n"
    "          value\n          id\n        }\n      }\n    }\n  }\n}"
)

RATINGS_QUERY_STRING = (
    "query RatingsListQuery(\n  $count: Int!\n  $id: ID!\n  $courseFilter: String\n"
    "  $cursor: String\n) {\n  node(id: $id) {\n    __typename\n"
    "    ... on Teacher {\n      ...RatingsList_teacher_4pguUW\n    }\n    id\n  }\n}\n\n"
    "fragment CourseMeta_rating on Rating {\n  attendanceMandatory\n  wouldTakeAgain\n"
    "  grade\n  textbookUse\n  isForOnlineClass\n  isForCredit\n}\n\n"
    "fragment RatingHeader_rating on Rating {\n  legacyId\n  date\n  class\n"
    "  helpfulRating\n  clarityRating\n  isForOnlineClass\n}\n\n"
    "fragment RatingValues_rating on Rating {\n  helpfulRating\n  clarityRating\n"
    "  difficultyRating\n}\n\n"
    "fragment RatingTags_rating on Rating {\n  ratingTags\n}\n\n"
    "fragment RatingFooter_rating on Rating {\n  id\n  comment\n  adminReviewedAt\n"
    "  flagStatus\n  legacyId\n  thumbsUpTotal\n  thumbsDownTotal\n  thumbs {\n"
    "    thumbsUp\n    thumbsDown\n    computerId\n    id\n  }\n  teacherNote {\n"
    "    id\n  }\n}\n\n"
    "fragment Rating_rating on Rating {\n  comment\n  flagStatus\n  createdByUser\n"
    "  teacherNote {\n    id\n  }\n  ...RatingHeader_rating\n  ...RatingValues_rating\n"
    "  ...CourseMeta_rating\n  ...RatingTags_rating\n  ...RatingFooter_rating\n}\n\n"
    "fragment RatingsList_teacher_4pguUW on Teacher {\n  id\n  legacyId\n  lastName\n"
    "  numRatings\n  school {\n    id\n    legacyId\n    name\n    city\n    state\n"
    "    avgRating\n    numRatings\n  }\n  ...Rating_teacher\n"
    "  ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {\n"
    "    edges {\n      cursor\n      node {\n        ...Rating_rating\n        id\n"
    "        __typename\n      }\n    }\n    pageInfo {\n      hasNextPage\n"
    "      endCursor\n    }\n  }\n}\n\n"
    "fragment Rating_teacher on Teacher {\n  id\n  legacyId\n  lockStatus\n"
    "  isProfCurrentUser\n}\n"
)


# ---------------------------------------------------------------------------
# Variable builders
# ---------------------------------------------------------------------------


def build_professor_variables(cursor: str) -> Dict[str, Any]:
    """Builds the variables dict for one page of the professor search query.

    Args:
        cursor: The pagination cursor for the requested page.

    Returns:
        A variables dict ready to pass to the GraphQL client.
    """
    return {
        "count": _PROFESSOR_PAGE_SIZE,
        "cursor": cursor,
        "query": {"text": "", "schoolID": _UCF_SCHOOL_ID, "fallback": True},
    }


def build_review_variables(prof_id: str, cursor: str) -> Dict[str, Any]:
    """Builds the variables dict for one page of ratings for a professor.

    Args:
        prof_id: The RMP professor node ID.
        cursor: The pagination cursor for the requested page.

    Returns:
        A variables dict ready to pass to the GraphQL client.
    """
    return {
        "count": _REVIEW_PAGE_SIZE,
        "id": prof_id,
        "courseFilter": None,
        "cursor": cursor,
    }
