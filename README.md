<h1 align="center"><img src="./assets/logo.gif" width="30px"> PenguinTunes <img src="./assets/logo.gif" width="30px"></h1>

## ✨Latest Updates

v1.0.0 Is out!

## 🚧 | Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/)

## 🥚 | Tutorial

- You need to set following environment variables in your system before progressing
  - DISCORD_TOKEN: Your discord bot token, that can be generated on a new application on [Discord Developer Portal](https://discord.com/developers/applications?new_application=true)
  - LAVALINK_HOST: If using the one that gets automatically spun-up on `docker compose up`, set this to `http://lavalink`, else, set this to your preferred one
  - LAVALINK_PORT: If using the one that gets automatically spun-up on `docker compose up`, set this to `2333`, else, set this to your preferred one
  - LAVALINK_PASSWORD: Define your LAVALINK_PASSWORD or pass the one you need to connect to the external Lavalink server
  - SPOTIFY_CLIENT_ID: Get one from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) after creating a new application.
  - SPOTIFY_CLIENT_SECRET: Get one from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) after creating a new application.
- To run the bot, after all environment variables have been set up. Run `docker compose up --build` (add `-d` if you wish to run it dettached)
- If you do not wish to run lavalink locally, you can also run `docker compose up penguintunes --build` (add `-d` if you wish to run it dettached)
- Documentation is mostly AI Generated. If there any egregious errors in it, please open an Issue
