FROM python:3.13-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir pyyaml==6.0.2 markdown==3.7
COPY scripts/ scripts/
COPY records/ records/
COPY schema/ schema/
COPY site/ site/
RUN python site/build.py

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/site/_site/ /srv/
EXPOSE 8080
