# This explicit base-image version and manifest digest are fixed at controlled
# build time. The final registered image identity must use its own registry
# manifest digest, never a tag or local image ID alone.
FROM python:3.12.11-alpine3.22@sha256:efcdfa6a6b2fd2afb9c7dfa9a5b288a6f68338b5cfdebe6b637d986067d85757

# The image deliberately installs no packages. The standard-library unittest
# runner is sufficient for the sole registered fixture command.
RUN addgroup -S fixture && adduser -S -G fixture -h /workspace fixture

WORKDIR /workspace
USER fixture

# The OCI adapter supplies the approved structured command. No shell entrypoint
# or default command is provided by this image.
ENTRYPOINT []
CMD []
