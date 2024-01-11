.PHONY: docker-build docker-run docker-up

docker-build:
	docker build --build-arg TOKEN=$(DISCORD_TOKEN) -t piplup:latest .

docker-run:
	docker run -d --restart unless-stopped piplup:latest

docker-up: docker-build docker-run
