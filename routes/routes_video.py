from routes import main_blueprint
from .common_imports import *

# 🛠️ Fetch All YouTube Videos (API)
@main_blueprint.route("/api/youtube_videos", methods=["GET"])
@login_required
def get_youtube_videos_api():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    query = YouTubeVideo.query
    
    # Apply filters if present
    search_query = request.args.get('q')
    if search_query:
        query = query.filter(
            or_(
                YouTubeVideo.title.ilike(f'%{search_query}%'),
                YouTubeVideo.youtube_id.ilike(f'%{search_query}%')
            )
        )
    
    visibility_filter = request.args.get("visibility", "all")
    usage_filter = request.args.get("usage", "all")
    if visibility_filter == "visible":
        query = query.filter(YouTubeVideo.is_visible == True)
    elif visibility_filter == "hidden":
        query = query.filter(YouTubeVideo.is_visible == False)
    if usage_filter == "used":
        query = query.filter(YouTubeVideo.news.any())
    elif usage_filter == "unused":
        query = query.filter(~YouTubeVideo.news.any())
    
    # Get pagination object
    pagination = query.order_by(YouTubeVideo.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Cache YouTube metadata if API key is available
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        for video in pagination.items:
            if not video.title:  # Only fetch if title is missing
                try:
                    r = requests.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "id": video.youtube_id,
                            "part": "snippet",
                            "key": api_key,
                        },
                        timeout=5  # Add timeout for better performance
                    )
                    items = r.json().get("items") or []
                    if items:
                        sn = items[0].get("snippet", {})
                        video.title = sn.get("title")
                        db.session.commit()
                except requests.exceptions.RequestException:
                    pass
    
    return jsonify({
        'items': [video.to_dict() for video in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    })


# 🛠️ Fetch a Single YouTube Video (API)
@main_blueprint.route("/api/youtube_videos/<int:video_id>", methods=["GET"])
def get_youtube_video(video_id):
    video = YouTubeVideo.query.get_or_404(video_id)
    
    # Cache YouTube metadata if API key is available and title is missing
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key and not video.title:
        try:
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "id": video.youtube_id,
                    "part": "snippet",
                    "key": api_key,
                },
                timeout=5
            )
            items = r.json().get("items") or []
            if items:
                sn = items[0].get("snippet", {})
                video.title = sn.get("title")
                db.session.commit()
        except requests.exceptions.RequestException:
            pass
    
    return jsonify(video.to_dict())


# 🛠️ Add a YouTube Video (API)
@main_blueprint.route("/api/youtube_videos", methods=["POST"])
@login_required
def add_youtube_video():
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    data = request.get_json()
    link = data.get("link")

    if not link:
        return jsonify({"error": "Video link is required"}), 400

    # extract YouTube ID from link
    m = re.search(
        r"(?:https?://)?(?:www\.)?(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/))([A-Za-z0-9_-]{11})",
        link,
    )
    if not m:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    youtube_id = m.group(1)

    # Check if video already exists
    if YouTubeVideo.query.filter_by(youtube_id=youtube_id).first():
        return jsonify({"error": "Video with this YouTube ID already exists"}), 400
    if YouTubeVideo.query.filter_by(link=link).first():
        return jsonify({"error": "Video with this YouTube ID already exists"}), 400

    # Create entry with extracted ID and link
    video = YouTubeVideo(youtube_id=youtube_id, link=link, user_id=current_user.id)

    # fetch metadata via YouTube Data API (if key present)
    api_key = os.getenv("YOUTUBE_API_KEY")
    if api_key:
        try:
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "id": youtube_id,
                    "part": "snippet,contentDetails",
                    "key": api_key,
                },
                timeout=5
            )
            items = r.json().get("items") or []
            if items:
                sn = items[0].get("snippet", {})
                cd = items[0].get("contentDetails", {})
                video.title = sn.get("title")
                dur = cd.get("duration")
                if dur:
                    video.duration = parse_iso8601_duration(dur)
        except requests.exceptions.RequestException:
            pass
    # fallback to oEmbed for title
    if not video.title:
        try:
            o = requests.get(
                f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={youtube_id}&format=json",
                timeout=5
            )
            video.title = o.json().get("title")
        except requests.exceptions.RequestException:
            pass

    try:
        db.session.add(video)
        db.session.commit()
        return jsonify({"message": "Video added successfully", "id": video.id}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# 🛠️ Update a YouTube Video (API)
@main_blueprint.route("/api/youtube_videos/<int:video_id>", methods=["PUT"])
@login_required
def update_youtube_video(video_id):
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    video = YouTubeVideo.query.get_or_404(video_id)
    data = request.get_json()

    youtube_id = data.get("youtube_id")
    link = data.get("link")

    # Update fields if provided
    if youtube_id and youtube_id != video.youtube_id:
        if YouTubeVideo.query.filter_by(youtube_id=youtube_id).first():
            return jsonify(
                {"error": "Another video with this YouTube ID already exists"}
            ), 400
        video.youtube_id = youtube_id

    if link and link != video.link:
        if YouTubeVideo.query.filter_by(link=link).first():
            return jsonify(
                {"error": "Another video with this link already exists"}
            ), 400
        video.link = link

    try:
        db.session.commit()
        return jsonify({"message": "Video updated successfully"}), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# 🛠️ Toggle YouTube Video Visibility (API)
@main_blueprint.route(
    "/api/youtube_videos/<int:video_id>/visibility", methods=["PATCH"]
)
@login_required
def toggle_youtube_video_visibility(video_id):
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    video = YouTubeVideo.query.get_or_404(video_id)
    data = request.get_json()

    if "is_visible" not in data:
        return jsonify({"error": "is_visible field is required"}), 400

    video.is_visible = data["is_visible"]
    db.session.commit()

    return jsonify({"message": "Visibility updated successfully"}), 200


# 🛠️ Delete a YouTube Video (API)
@main_blueprint.route("/api/youtube_videos/<int:video_id>", methods=["DELETE"])
@login_required
def delete_youtube_video(video_id):
    if not current_user.is_owner() and current_user.role != UserRole.ADMIN:
        abort(403)

    video = YouTubeVideo.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()

    return jsonify({"message": "Video deleted successfully"}), 200


# 🛠️ Bulk Delete YouTube Videos (API)
@main_blueprint.route("/api/youtube_videos/bulk-delete", methods=["POST"])
@login_required
def bulk_delete_youtube_videos():
    data = request.get_json()
    ids = data.get("ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    videos_to_delete = YouTubeVideo.query.filter(YouTubeVideo.id.in_(ids)).all()
    deleted_count = 0
    for video in videos_to_delete:
        if video.user_id == current_user.id or current_user.role in [UserRole.ADMIN, UserRole.SUPERUSER]:
            db.session.delete(video)
            deleted_count += 1
    db.session.commit()
    return jsonify({"deleted": deleted_count}), 200

# 🛠️ Bulk Update YouTube Videos Visibility (API)
@main_blueprint.route("/api/youtube_videos/bulk-visibility", methods=["POST"])
@login_required
def bulk_update_youtube_videos_visibility():
    data = request.get_json()
    ids = data.get("ids", [])
    is_visible = data.get("is_visible")
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({"error": "Invalid or missing 'ids'"}), 400
    if not isinstance(is_visible, bool):
        return jsonify({"error": "'is_visible' must be a boolean"}), 400
    videos_to_update = YouTubeVideo.query.filter(YouTubeVideo.id.in_(ids)).all()
    updated_count = 0
    for video in videos_to_update:
        if video.user_id == current_user.id or current_user.role in [UserRole.ADMIN, UserRole.SUPERUSER]:
            video.is_visible = is_visible
            updated_count += 1
    db.session.commit()
    return jsonify({"updated": updated_count}), 200


# 🛠️ Fetch Latest YouTube Videos for Frontend (Public API)
@main_blueprint.route("/api/youtube_videos/latest", methods=["GET"])
def get_latest_youtube_videos():
    limit = request.args.get("limit", default=6, type=int)
    videos = (
        YouTubeVideo.query.filter_by(is_visible=True)
        .order_by(YouTubeVideo.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify([video.to_dict() for video in videos])
