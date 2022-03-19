PYTHON            := python
VERSION_FILE      := ./src/midori/_version.py
VERSION           := $(shell grep __version__ ${VERSION_FILE} | cut -d " " -f 3 ${VERSION_FILE} | tr -d '"')
COMMIT_HASH       := $(shell git rev-parse --short HEAD)
DOCKER_REGISTRY   := docker.io
DOCKER_OWNER      := midori
DOCKER_APP_BASE	  := base
DOCKER_APP	  := midori
DOCKER_TAG        := ${VERSION}
DOCKER_BASE_IMAGE := ${DOCKER_OWNER}/${DOCKER_APP_BASE}:${DOCKER_TAG}
DOCKER_IMAGE      := ${DOCKER_OWNER}/${DOCKER_APP}:${DOCKER_TAG}

ifdef GUNICORN_WORKERS
NO_OF_GUNICORN_WORKERS := $(GUNICORN_WORKERS)
else
NO_OF_GUNICORN_WORKERS := 5
endif

.PHONY: help clean install test build image publish
.DEFAULT_GOAL = help

#help: List available tasks on this project
help:
	@grep -E '^#[a-zA-Z\.\-]+:.*$$' $(MAKEFILE_LIST) | tr -d '#' | awk 'BEGIN {FS = ": "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

#version: Show current version of appstore
version:
	echo ${VERSION}

#clean: Remove old build artifacts and installed packages
clean:
	${PYTHON} -m pip uninstall -y -r requirements.txt

#install: Install application along with required development packages
install:
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install -r requirements.txt

#test: Run all tests
test:
	echo test

#start: Run the gunicorn server
start:
	gunicorn --bind 0.0.0.0:8000 --log-level=debug --pythonpath=./src midori.api:app --workers=${NO_OF_GUNICORN_WORKERS}

#build: Build the Docker image
build.base:

	docker build --no-cache -t ${DOCKER_IMAGE} -f Dockerfile-base .
	 # docker build --no-cache --pull -t ${DOCKER_IMAGE} -f Dockerfile-base .
	 # docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_BASE_IMAGE}
	 # docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_BASE_IMAGE}-${COMMIT_HASH}

build.midori:
	docker build --no-cache -t ${DOCKER_IMAGE} -f Dockerfile .
	 # docker build --no-cache --pull -t ${DOCKER_IMAGE} -f Dockerfile .
	 # docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
	 # docker tag ${DOCKER_IMAGE} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}-${COMMIT_HASH}

build: build.base build.midori

#build.test: Test the Docker image (requires docker compose)
build.test:
	echo docker-compose -f docker-compose.test.yml up --build --exit-code-from appstore

#publish.image: Push the Docker image
publish: build
	echo docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}
	echo docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}-${COMMIT_HASH}

