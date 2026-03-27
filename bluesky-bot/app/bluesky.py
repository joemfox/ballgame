"""
Thin wrapper around the atproto client.
"""
import os
import re
from atproto import Client, models


def login() -> Client:
    client = Client()
    client.login(
        os.environ["BLUESKY_HANDLE"],
        os.environ["BLUESKY_APP_PASSWORD"],
    )
    return client


_TAG_RE = re.compile(rb"(?:^|\s)(#[^\d\s]\S*)", re.MULTILINE)


def _parse_facets(text: str) -> list | None:
    """Return a list of hashtag facets for all #tags in text, or None if none found."""
    facets = []
    text_bytes = text.encode("utf-8")
    for m in _TAG_RE.finditer(text_bytes):
        tag_bytes = m.group(1)
        byte_start = m.start(1)
        # Strip trailing punctuation (., ! ? ; :) per Bluesky spec
        tag_str = tag_bytes.decode("utf-8").rstrip(".,!?;:")
        byte_end = byte_start + len(tag_str.encode("utf-8"))
        tag_name = tag_str[1:]  # strip leading #
        facets.append(
            models.AppBskyRichtextFacet.Main(
                index=models.AppBskyRichtextFacet.ByteSlice(
                    byte_start=byte_start,
                    byte_end=byte_end,
                ),
                features=[models.AppBskyRichtextFacet.Tag(tag=tag_name)],
            )
        )
    return facets or None


def post(client: Client, text: str) -> None:
    client.send_post(text=text, facets=_parse_facets(text))


def post_image(client: Client, text: str, image_bytes: bytes, alt_text: str = "") -> None:
    response = client.upload_blob(image_bytes)
    client.send_post(
        text=text,
        facets=_parse_facets(text),
        embed=models.AppBskyEmbedImages.Main(
            images=[
                models.AppBskyEmbedImages.Image(
                    image=response.blob,
                    alt=alt_text,
                )
            ]
        ),
    )
