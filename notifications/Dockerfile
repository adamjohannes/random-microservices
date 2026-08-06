FROM haskell:9.8 AS build
WORKDIR /app

COPY notifications.cabal cabal.project* ./
RUN cabal update && cabal build --only-dependencies -j4

COPY . .
RUN cabal build exe:notifications -j4
RUN cp $(cabal list-bin notifications) /app/notifications-exe

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y libgmp10 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app/notifications-exe ./notifications
EXPOSE 8083
ENTRYPOINT ["./notifications"]
