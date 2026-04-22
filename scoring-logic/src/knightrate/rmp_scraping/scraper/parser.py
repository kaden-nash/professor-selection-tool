from typing import List, Dict, Any, Tuple

from .models import Professor, Rating


def parse_professors(data: Dict[str, Any]) -> Tuple[List[Professor], Dict[str, Any], int]:
    """Parses the GraphQL response from the teacher search query.

    Args:
        data: The raw JSON response dict from the GraphQL client.

    Returns:
        A tuple of (professors, pageInfo dict, resultCount).
    """
    teachers_data = data.get("data", {}).get("search", {}).get("teachers", {})
    edges = teachers_data.get("edges", [])

    professors = [_parse_professor_node(edge.get("node", {})) for edge in edges]
    professors = [p for p in professors if p is not None]

    page_info = teachers_data.get("pageInfo", {"hasNextPage": False, "endCursor": ""})
    result_count = teachers_data.get("resultCount", 0)

    return professors, page_info, result_count


def parse_ratings(data: Dict[str, Any]) -> Tuple[List[Rating], Dict[str, Any]]:
    """Parses the GraphQL response from the teacher ratings query.

    Args:
        data: The raw JSON response dict from the GraphQL client.

    Returns:
        A tuple of (ratings, pageInfo dict).
    """
    node_data = data.get("data", {}).get("node", {})
    ratings_data = node_data.get("ratings", {})
    edges = ratings_data.get("edges", [])

    ratings = [_parse_rating_node(edge.get("node", {})) for edge in edges]
    ratings = [r for r in ratings if r is not None]

    page_info = ratings_data.get("pageInfo", {"hasNextPage": False, "endCursor": ""})
    return ratings, page_info


def _parse_professor_node(node: Dict[str, Any]) -> "Professor | None":
    """Parses a single professor edge node into a Professor object.

    Args:
        node: The raw node dict from the GraphQL edge.

    Returns:
        A Professor instance, or None if parsing fails.
    """
    try:
        return Professor(**node)
    except Exception as exc:
        print(f"Failed to parse professor node: {exc}")
        return None


def _parse_rating_node(node: Dict[str, Any]) -> "Rating | None":
    """Parses a single rating edge node into a Rating object.

    Args:
        node: The raw node dict from the GraphQL edge.

    Returns:
        A Rating instance, or None if parsing fails.
    """
    node["ratingTags"] = _normalize_rating_tags(node.get("ratingTags"))
    try:
        return Rating(**node)
    except Exception as exc:
        print(f"Failed to parse rating node: {exc}")
        return None


def _normalize_rating_tags(tags: Any) -> List[str]:
    """Normalises the ratingTags field into a list of strings.

    RMP returns ratingTags as either a ``--``-delimited string or already a list.
    This function ensures the result is always a clean list.

    Args:
        tags: The raw ratingTags value from the API response.

    Returns:
        A list of tag strings.
    """
    if isinstance(tags, str):
        return [tag.strip() for tag in tags.split("--") if tag.strip()]
    if isinstance(tags, list):
        return tags
    return []
