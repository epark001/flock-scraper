FLOCK_AUTH_FILE=secrets/tikee_auth.json
FLOCK_AUTH_PAYLOAD=$(shell cat $(FLOCK_AUTH_FILE))

GCP_CREDS_FILE=secrets/gcp_creds.json
GCP_CREDS=$(shell cat $(GCP_CREDS_FILE))

VADE_CRUD_API_KEY_FILE=secrets/vade_crud_api_key
VADE_CRUD_API_KEY=$(shell cat $(VADE_CRUD_API_KEY_FILE))

# Flock Scraper Image Commands

.PHONY: build
build:
	docker build -f Dockerfile -t gcr.io/vade-backend/flock-scraper .

.PHONY: push
push:
	docker tag gcr.io/vade-backend/flock-scraper gcr.io/vade-backend/flock-scraper:test
	docker push gcr.io/vade-backend/flock-scraper:test

.PHONY: run
run:
	docker kill tikee-scraper; true
	docker rm tikee-scraper; true
	docker run -it --name tikee-scraper \
		-e VADE_CRUD_API_KEY='$(VADE_CRUD_API_KEY)' \
		-e TIKEE_AUTH_PAYLOAD='$(FLOCK_AUTH_PAYLOAD)' \
		-e GCP_CREDS='$(GCP_CREDS)' \
		gcr.io/vade-backend/flock-scraper