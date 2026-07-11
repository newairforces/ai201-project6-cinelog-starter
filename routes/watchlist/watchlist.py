"""
routes/watchlist/watchlist.py — CineLog

Endpoints for a user's watchlist (films they want to watch later).
"""

from flask import Blueprint, jsonify, request
from services.watchlist_service import (
    add_to_watchlist,
    update_watchlist_visibility,
    get_watchlist,
    FilmNotFoundError,
    AlreadyInWatchlistError,
    NotInWatchlistError,
)

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """
    GET /watchlist/<user_id>

    Returns all films in a user's watchlist, sorted newest-first.
    """
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    POST /watchlist/<user_id>/add

    Body: { "film_id": "<uuid>", "public": true }  (public optional)
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

    try:
        entry = add_to_watchlist(
            user_id=user_id,
            film_id=data["film_id"],
            public=data.get("public", True),
        )
        return jsonify(entry.to_dict()), 201
    except FilmNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except AlreadyInWatchlistError as e:
        return jsonify({"error": str(e)}), 409


@watchlist_bp.route("/<user_id>/visibility", methods=["PATCH"])
def update_visibility(user_id):
    """
    PATCH /watchlist/<user_id>/visibility

    Body: { "film_id": "<uuid>", "public": true }
    """
    data = request.get_json()
    if not data or "film_id" not in data or "public" not in data:
        return jsonify({"error": "film_id and public are required"}), 400

    try:
        entry = update_watchlist_visibility(
            user_id=user_id,
            film_id=data["film_id"],
            public=bool(data["public"]),
        )
        return jsonify(entry.to_dict()), 200
    except NotInWatchlistError as e:
        return jsonify({"error": str(e)}), 404
