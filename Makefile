VENV 	?= venv
PYTHON 	= $(VENV)/bin/python3.9
PIP		= $(VENV)/bin/pip

# Variables used to configure
IMAGE_REGISTRY_DOCKERHUB 	?= maciuozz
IMAGE_REGISTRY_GHCR		?= ghcr.io
IMAGE_REPO			=  keepcodingclouddevops7
IMAGE_NAME			?= kc7-sre-practica-final
VERSION				?= develop

# Variables used to configure docker images registries to build and push
IMAGE			= $(IMAGE_REGISTRY_DOCKERHUB)/$(IMAGE_REPO)/$(IMAGE_NAME):$(VERSION)
IMAGE_LATEST	        = $(IMAGE_REGISTRY_DOCKERHUB)/$(IMAGE_REPO)/$(IMAGE_NAME):latest
IMAGE_GHCR		= $(IMAGE_REGISTRY_GHCR)/$(IMAGE_REPO)/$(IMAGE_NAME):$(VERSION)
IMAGE_GHCR_LATEST       = $(IMAGE_REGISTRY_GHCR)/$(IMAGE_REPO)/$(IMAGE_NAME):latest

.PHONY: run
run: $(VENV)/bin/activate
	$(PYTHON) src/app.py

.PHONY: unit-test
unit-test: $(VENV)/bin/activate
	pytest

.PHONY: unit-test-coverage
unit-test-coverage: $(VENV)/bin/activate
	pytest --cov

.PHONY: $(VENV)/bin/activate
$(VENV)/bin/activate: requirements.txt
	python3.9 -m venv $(VENV)
	$(PIP) install -r requirements.txt

.PHONY: docker-build
docker-build: ## Build image
    
	@echo "$(IMAGE)..."
	@echo "$(IMAGE_LATEST)..."
	@echo "$(IMAGE_GHCR)..."
	@echo "$(IMAGE_GHRC_LATEST)..."
	docker build -t $(IMAGE) -t $(IMAGE_LATEST) -t $(IMAGE_GHCR) -t $(IMAGE_GHRC_LATEST) .

.PHONY: publish
publish: docker-build ## Publish image
	docker push $(IMAGE)
	docker push $(IMAGE_LATEST)
	docker push $(IMAGE_GHCR)
	docker push $(IMAGE_GHRC_LATEST)
