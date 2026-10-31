from typing import Optional
from fastapi import APIRouter, Query
from backend.integrations.music_player import music_player
from backend.schemas.models import SpotifyPlayRequest, SpotifySearchRequest

router = APIRouter(prefix="/api/music", tags=["Music & Audio Streaming"])

@router.post("/play")
def play_music(request: SpotifyPlayRequest):
    """
    Initiates free YouTube audio streaming for a song, artist, or query.
    """
    return music_player.play(
        query=request.query,
        track=request.track,
        artist=request.artist
    )

@router.post("/pause")
def pause_music():
    """
    Pauses music playback.
    """
    return music_player.pause()

@router.post("/resume")
def resume_music():
    """
    Resumes music playback.
    """
    return music_player.resume()

@router.post("/stop")
def stop_music():
    """
    Stops music playback and releases player resources.
    """
    return music_player.stop()

@router.post("/next")
def next_music():
    """
    Skips current track.
    """
    return music_player.next_track()

@router.post("/volume")
def set_music_volume(volume: int = Query(..., ge=0, le=100)):
    """
    Sets music volume (0-100).
    """
    return music_player.set_volume(volume)

@router.get("/status")
def music_status():
    """
    Gets real-time playback telemetry.
    """
    return music_player.get_status()

@router.post("/search")
def search_music(request: SpotifySearchRequest):
    """
    Searches free YouTube catalog for songs.
    """
    return music_player.search(query=request.query, limit=5)

