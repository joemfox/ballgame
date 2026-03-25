"""
Uses the bot's own atproto repo as a state store.
One record per posted event. The atproto rkey is a composite of
season + event_type + game_id + player_id for O(1) duplicate checks.
The record body stores all fields as separate named values.
"""
from atproto import Client
from atproto_client.exceptions import RequestException

COLLECTION = "app.bsky.feed.postgate"


def _rkey(season: int, event_type: str, game_id: str, player_id: str) -> str:
    # atproto rkeys allow [a-zA-Z0-9._~-]
    raw = f"{season}-{event_type}-{game_id}-{player_id}"
    return "".join(c if c.isalnum() or c in "-._~" else "~" for c in raw)


def already_posted(
    client: Client,
    handle: str,
    season: int,
    event_type: str,
    game_id: str,
    player_id: str,
) -> bool:
    try:
        client.com.atproto.repo.get_record(
            params={
                "repo": handle,
                "collection": COLLECTION,
                "rkey": _rkey(season, event_type, game_id, player_id),
            }
        )
        return True
    except RequestException:
        return False


def mark_posted(
    client: Client,
    handle: str,
    season: int,
    event_type: str,
    game_id: str,
    player_id: str,
) -> None:
    rkey = _rkey(season, event_type, game_id, player_id)
    client.com.atproto.repo.put_record(
        data={
            "repo": handle,
            "collection": COLLECTION,
            "rkey": rkey,
            "record": {
                "$type": COLLECTION,
                "rkey": rkey,
                "season": season,
                "gameId": game_id,
                "playerId": player_id,
                "eventType": event_type,
            },
        }
    )
