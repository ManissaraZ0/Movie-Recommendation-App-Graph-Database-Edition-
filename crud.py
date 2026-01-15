from db import Neo4jConnection
from uuid import uuid4

conn = Neo4jConnection()

def create_review(data):
    review_id = str(uuid4())
    movie_id = str(uuid4())

    conn.query("""
        MERGE (u:User {username: $username})
        MERGE (m:Movie {title: $movie_title})
          ON CREATE SET 
            m.id = $movie_id,
            m.released = $year,
            m.genres = $genres
        CREATE (r:Review {
            id: $review_id,
            rating: $rating,
            comment: $comment
        })
        MERGE (u)-[:WROTE]->(r)
        MERGE (r)-[:REVIEWS]->(m)
        WITH m, $genres AS genreNames
        UNWIND genreNames AS genreName
        MERGE (g:Genre {name: genreName})
          ON CREATE SET g.id = randomUUID()
        MERGE (m)-[:IN_GENRE {id: randomUUID()}]->(g)
    """, parameters={
        "username": data.username,
        "movie_title": data.movie_title,
        "year": data.year,
        "rating": data.rating,
        "comment": data.comment,
        "genres": data.genres,
        "review_id": review_id,
        "movie_id": movie_id,
    })

def get_reviews_with_similar(movie_title):
    query = """
        MATCH (m:Movie)
        WHERE toLower(m.title) CONTAINS toLower($movie_title)
        OPTIONAL MATCH (u:User)-[:WROTE]->(r:Review)-[:REVIEWS]->(m)
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        RETURN collect(DISTINCT {
            id: r.id,
            user: u.username,
            rating: r.rating,
            comment: r.comment,
            title: m.title,
            year: m.released,
            genres: m.genres
        }) AS reviews, collect(DISTINCT g.name) AS genres
    """
    result = conn.query(query, {"movie_title": movie_title})
    if not result:
        return {"reviews": [], "similar_movies": []}

    genres = result[0]["genres"]

    similar_query = """
        MATCH (other:Movie)-[:IN_GENRE]->(g:Genre)
        WHERE g.name IN $genres
          AND NOT toLower(other.title) CONTAINS toLower($movie_title)
        RETURN DISTINCT other.title AS title, other.released AS year, other.genres AS genres
        LIMIT 10
    """
    similar_movies = conn.query(similar_query, {"genres": genres, "movie_title": movie_title})

    return {
        "reviews": [dict(r) for r in result[0]["reviews"] if r["id"] is not None],
        "similar_movies": [dict(m) for m in similar_movies]
    }

def update_review(review_id, summary, rating):
    query = """
        MATCH (r:Review {id: $review_id})
        SET r.comment = $comment,
            r.rating = $rating
    """
    conn.query(query, {
        "review_id": review_id,
        "comment": summary,
        "rating": rating
    })

def delete_review(review_id):
    query = """
        MATCH (r:Review {id: $review_id})-[rel]-()
        DELETE rel, r
    """
    conn.query(query, {"review_id": review_id})
