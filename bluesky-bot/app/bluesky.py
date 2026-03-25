"""
Thin wrapper around the atproto client.
"""
import os
from atproto import Client, models


def login() -> Client:
    client = Client()
    client.login(
        os.environ["BLUESKY_HANDLE"],
        os.environ["BLUESKY_APP_PASSWORD"],
    )
    return client


def post(client: Client, text: str) -> None:
    client.send_post(text=text)


def post_image(client: Client, text: str, image_bytes: bytes, alt_text: str = "") -> None:
    response = client.upload_blob(image_bytes)
    client.send_post(
        text=text,
        embed=models.AppBskyEmbedImages.Main(
            images=[
                models.AppBskyEmbedImages.Image(
                    image=response.blob,
                    alt=alt_text,
                )
            ]
        ),
    )
