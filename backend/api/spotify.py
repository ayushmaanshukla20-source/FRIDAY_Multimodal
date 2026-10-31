from typing import Optional
from fastapi import APIRouter, Query
from backend.schemas.models import (
    SpotifySearchRequest, SpotifySearchResponse, SpotifyItem,
    SpotifyPlayRequest, SpotifyPlaylistRequest
)
from backend.integrations.spotify import spotify_integration

router = APIRouter(prefix="/api/spotify", tags=["Spotify Integration"])

@router.post("/search", response_model=SpotifySearchResponse)
def search_spotify(request: SpotifySearchRequest):
    """
    Searches for audio tracks or returns direct Spotify playback URIs.
    """
    res = spotify_integration.search(query=request.query, search_type=request.search_type)
    items = [SpotifyItem(**it) for it in res.get("items", [])]

    return SpotifySearchResponse(
        query=request.query,
        items=items,
        is_authenticated=res.get("is_authenticated", False),
        message=res.get("message", "")
    )

@router.post("/play")
def play_spotify(request: SpotifyPlayRequest):
    """
    Triggers track playback on Spotify.
    """
    return spotify_integration.play(
        query=request.query,
        track=request.track,
        artist=request.artist
    )

@router.post("/pause")
def pause_spotify():
    """
    Pauses Spotify playback.
    """
    return spotify_integration.pause()

@router.post("/resume")
def resume_spotify():
    """
    Resumes Spotify playback.
    """
    return spotify_integration.resume()

@router.post("/next")
def next_spotify():
    """
    Skips to the next Spotify track.
    """
    return spotify_integration.next_track()

@router.post("/stop")
def stop_spotify():
    """
    Stops audio playback.
    """
    from backend.integrations.music_player import music_player
    return music_player.stop()

@router.post("/volume")
def set_spotify_volume(volume: int = Query(..., ge=0, le=100)):
    """
    Sets audio volume (0-100).
    """
    from backend.integrations.music_player import music_player
    return music_player.set_volume(volume)

@router.post("/playlist")
def play_playlist(request: SpotifyPlaylistRequest):
    """
    Plays a Spotify playlist.
    """
    return spotify_integration.play_playlist(request.playlist_name)

@router.get("/status")
def spotify_status():
    """
    Retrieves current Spotify playback telemetry and connection status.
    """
    return spotify_integration.get_playback_status()

@router.get("/auth-url")
def get_auth_url():
    """
    Retrieves Spotify OAuth authorization URL.
    """
    url = spotify_integration.get_auth_url()
    return {"auth_url": url, "configured": bool(url)}

@router.get("/callback")
def spotify_callback(code: str = Query(...)):
    """
    Handles OAuth callback code from Spotify.
    """
    success = spotify_integration.save_auth_code(code)
    return {"success": success, "message": "Spotify authentication completed." if success else "Failed to authenticate with Spotify."}

