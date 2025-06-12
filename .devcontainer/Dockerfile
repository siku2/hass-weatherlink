FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm

# Add go2rtc
COPY --from=alexxit/go2rtc:latest /usr/local/bin/go2rtc /usr/local/bin/go2rtc

RUN <<EOF
set -eux

# We're adding these packages because Home Assistant core components rely on them.
# It can still start without them, but it will throw warnings.
DEPENDENCIES="libpcap0.8 libturbojpeg0-dev ffmpeg"

apt-get update
apt-get install -y --no-install-recommends $DEPENDENCIES
EOF
