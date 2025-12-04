from datetime import datetime
from db_connections import get_mongo_db_collection


def submit_performance_review(employee_id, review_date, reviewer_name,
                              overall_rating, strengths=None,
                              areas_for_improvement=None, comments="",
                              goals_for_next_period=None):
    """Submit a performance review for an employee."""
    try:
        collection = get_mongo_db_collection()

        review_document = {
            "employee_id": employee_id,
            "review_date": review_date,
            "reviewer_name": reviewer_name,
            "overall_rating": overall_rating,
            "strengths": strengths if strengths else [],
            "areas_for_improvement": areas_for_improvement if areas_for_improvement else [],
            "comments": comments,
            "goals_for_next_period": goals_for_next_period if goals_for_next_period else []
        }

        result = collection.insert_one(review_document)
        return result.inserted_id

    except Exception as e:
        print(f"Error submitting review: {e}")
        return None


def get_performance_reviews_for_employee(employee_id):
    """Get all performance reviews for a specific employee."""
    try:
        collection = get_mongo_db_collection()

        reviews = list(collection.find(
            {"employee_id": employee_id}
        ).sort("review_date", -1))

        # Convert ObjectId to string for JSON serialization
        for review in reviews:
            review['_id'] = str(review['_id'])

        return reviews

    except Exception as e:
        print(f"Error getting reviews: {e}")
        return []
