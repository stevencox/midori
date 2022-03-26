PYTHON            := python
PIP               := pip
VERSION_FILE      := ./src/midori/_version.py
VERSION           := $(shell grep __version__ ${VERSION_FILE} | cut -d " " -f 3 ${VERSION_FILE} | tr -d '"')
COMMIT_HASH       := $(shell git rev-parse --short HEAD)
CONTAINER_REGISTRY   := docker.io
CONTAINER_OWNER      := midori
CONTAINER_APP_WORKER := worker
CONTAINER_APP	       := api
CONTAINER_TAG          := ${VERSION}
CONTAINER_WORKER_IMAGE := ${CONTAINER_OWNER}/${CONTAINER_APP_WORKER}:${CONTAINER_TAG}
CONTAINER_IMAGE        := ${CONTAINER_OWNER}/${CONTAINER_APP}:${CONTAINER_TAG}

ifdef GUNICORN_WORKERS
NO_OF_GUNICORN_WORKERS := $(GUNICORN_WORKERS)
else
NO_OF_GUNICORN_WORKERS := 5
endif

.PHONY: help version clean install test docs build image publish
.DEFAULT_GOAL = help

#help: List available tasks on this project
help:
	@grep -E '^#[a-zA-Z\.\-]+:.*$$' $(MAKEFILE_LIST) | tr -d '#' | awk 'BEGIN {FS = ": "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

#version: Show current version of appstore
version:
	echo ${VERSION}

#clean: Remove old build artifacts and installed packages
clean:
	bin/midori configure clean

#install: Install application along with required development packages
install:
	bin/midori configure install

# Record existing requirements in requirements.txt
freeze:
	bin/midori configure freeze

#test: Run all tests
test:
	bin/midori test src

# Generate navigable documentation from the source code.
docs:
	bin/midori doc

#start: Run the gunicorn server
start:
	bin/midori serve ${NO_OF_GUNICORN_WORKERS}

#build: Build container image
build.worker:
	docker build --no-cache -t ${CONTAINER_WORKER_IMAGE} -f Dockerfile-worker .
	 # docker build --no-cache --pull -t ${CONTAINER_WORKER_IMAGE} -f Dockerfile-worker .
	 # docker tag ${CONTAINER_IMAGE} ${CONTAINER_REGISTRY}/${CONTAINER_WORKER_IMAGE}
	 # docker tag ${CONTAINER_IMAGE} ${CONTAINER_REGISTRY}/${CONTAINER_WORKER_IMAGE}-${COMMIT_HASH}

build.api:
	docker build --no-cache -t ${CONTAINER_IMAGE} -f Dockerfile-api .
	 # docker build --no-cache --pull -t ${CONTAINER_IMAGE} -f Dockerfile .
	 # docker tag ${CONTAINER_IMAGE} ${CONTAINER_REGISTRY}/${CONTAINER_IMAGE}
	 # docker tag ${CONTAINER_IMAGE} ${CONTAINER_REGISTRY}/${CONTAINER_IMAGE}-${COMMIT_HASH}

build: build.worker build.api

#build.test: Test the Container image (requires docker compose)
build.test:
	echo docker-compose -f docker-compose.test.yml up --build --exit-code-from appstore

#publish.image: Push the Docker image
publish: build
	echo docker push ${CONTAINER_REGISTRY}/${CONTAINER_IMAGE}
	echo docker push ${CONTAINER_REGISTRY}/${CONTAINER_IMAGE}-${COMMIT_HASH}

all: help version clean install test docs build 
