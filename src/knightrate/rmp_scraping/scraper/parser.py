from typing import List, Dict, Any, Tuple
from scraper.models import Professor, Rating  

def parse_professors(data: Dict[str, Any]) -> Tuple[List[Professor], Dict[str, Any], int]:
    """
    Parses the GraphQL response from the teacher search query.
    Returns a tuple of (List of Professors, pageInfo dict, resultCount).
    """
    teachers_data = data.get("data", {}).get("search", {}).get("teachers", {})
    edges = teachers_data.get("edges", [])
    
    professors = []
    for edge in edges:
        node = edge.get("node", {})
        # Note: GraphQL payload contains firstName, lastName, numRatings, avgDifficulty,
        # avgRating, department, id, wouldTakeAgainPercent, etc.
        try:
            prof = Professor(**node)
            professors.append(prof)
        except Exception as e:
            # Continue so one bad data node doesn't fail the whole parsing.
            print(f"Failed to parse professor node: {e}")
            pass
            
    page_info = teachers_data.get("pageInfo", {"hasNextPage": False, "endCursor": ""})
    result_count = teachers_data.get("resultCount", 0)
    
    return professors, page_info, result_count

def parse_ratings(data: Dict[str, Any]) -> Tuple[List[Rating], Dict[str, Any]]:
    """
    Parses the GraphQL response from the teacher ratings query.
    Returns a tuple of (List of Ratings, pageInfo dict).
    """
    node_data = data.get("data", {}).get("node", {})
    ratings_data = node_data.get("ratings", {})
    edges = ratings_data.get("edges", [])
    
    ratings_list = []
    for edge in edges:
        node = edge.get("node", {})
        
        # The prompt specifies: "Ensure that any data in 'ratingTags' is stored in the array 
        # that acts as the value of the 'ratingTags' field."
        # In the real RMP payload, ratingTags is often a single string delimited by "--".
        rating_tags = node.get("ratingTags")
        if isinstance(rating_tags, str):
            if rating_tags.strip():
                node["ratingTags"] = [tag.strip() for tag in rating_tags.split("--") if tag.strip()]
            else:
                node["ratingTags"] = []
        elif not isinstance(rating_tags, list):
            node["ratingTags"] = []
            
        try:
            rating = Rating(**node)
            ratings_list.append(rating)
        except Exception as e:
            print(f"Failed to parse rating node: {e}")
            pass
            
    page_info = ratings_data.get("pageInfo", {"hasNextPage": False, "endCursor": ""})
    
    return ratings_list, page_info
