FROM python:3.12-slim

WORKDIR /app

COPY bluesky-bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Convert woff fonts to TTF for Pillow/FreeType
RUN mkdir -p /app/assets/fonts
COPY app/ballgame/src/assets/fonts/GeistMono-Regular.woff /tmp/fonts/GeistMono-Regular.woff
COPY app/ballgame/src/assets/fonts/Geist-Bold.woff        /tmp/fonts/Geist-Bold.woff
RUN python -c "\
from fontTools.ttLib import TTFont; \
[(TTFont(f'/tmp/fonts/{n}.woff').save(f'/app/assets/fonts/{n}.ttf')) \
 for n in ['GeistMono-Regular', 'Geist-Bold']]" \
&& rm -rf /tmp/fonts

COPY bluesky-bot/app/ .

CMD ["sh"]
