.PHONY: test lint compile doc clean setup typecheck coverage check check-all gather-all

COLLECTIONS_PATH ?= /tmp/opencode
COLLECTION_LINK := $(COLLECTIONS_PATH)/ansible_collections/nokia/isam
ANSIBLE ?= $(shell if [ -x .venv/bin/ansible ]; then printf '%s' .venv/bin/ansible; else command -v ansible; fi)
INVENTORY ?= /home/jahknem/Projects/BlueNetworks/yplay-provisioning/inventory/production.yaml
VAULT_PASS ?= /home/jahknem/Projects/BlueNetworks/yplay-provisioning/.vault_pass
TARGET ?= DS-LIN-TEST-01
MODULES := $(patsubst plugins/modules/%.py,%,$(wildcard plugins/modules/isam_*.py))
RESOURCE_MODULES := $(filter-out isam_facts isam_security_ext_authenticator,$(MODULES))

setup:
	@mkdir -p $(COLLECTIONS_PATH)/ansible_collections/nokia
	@ln -sfn $(CURDIR) $(COLLECTION_LINK)
	@echo "Collection linked at $(COLLECTION_LINK)"

compile:
	python -m compileall plugins/module_utils plugins/modules tests/unit/modules

test: compile
	PYTHONPATH=$(COLLECTIONS_PATH) ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) \
		python -m pytest tests/unit/modules/network/isam -v $(ARGS)

coverage: compile
	PYTHONPATH=$(COLLECTIONS_PATH) ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) \
		python -m pytest tests/unit/modules/network/isam --cov=plugins/module_utils --cov-report=term

lint:
	@echo "=== flake8 ==="
	@flake8 plugins/ tests/ --max-line-length=160 --ignore=E122,E124,E126,E127,E128,E203,E225,E231,E265,E301,E302,E303,E305,E402,E501,E701,E702,E704,E741,F401,F403,F405,F811,F841,W291,W292,W293,W391,W503,W504 --statistics
	@echo "=== ansible-lint ==="
	@ansible-lint plugins/modules/

typecheck:
	@echo "=== mypy ==="
	@mypy plugins/module_utils/ plugins/modules/ --ignore-missing-imports --check-untyped-defs --disable-error-code=var-annotated --disable-error-code=assignment --disable-error-code=has-type --disable-error-code=index --disable-error-code=call-arg --disable-error-code=attr-defined

doc:
	@echo "=== ansible-doc validation ==="
	@failed=0; for m in $(MODULES) cli_config; do \
		ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) ansible-doc -t module nokia.isam.$$m > /dev/null 2>&1 && \
			echo "  OK nokia.isam.$$m" || { echo "  FAIL nokia.isam.$$m"; failed=1; }; \
	done; \
	ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) ansible-doc -t connection nokia.isam.isam_network_cli > /dev/null 2>&1 && \
		echo "  OK nokia.isam.isam_network_cli" || { echo "  FAIL nokia.isam.isam_network_cli"; failed=1; }; \
	exit $$failed

gather-all:
	@failed=0; for m in $(RESOURCE_MODULES); do \
		o=/tmp/opencode/live_$${m}_gathered.out; \
		ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) $(ANSIBLE) -i $(INVENTORY) $(TARGET) \
			--vault-password-file $(VAULT_PASS) -m nokia.isam.$$m -a 'state=gathered' \
			> $$o 2>&1; \
		rc=$$?; \
		if [ $$rc -eq 0 ]; then printf '  OK %s\n' "$$m"; \
		else printf '  FAIL %s (rc=%s)\n' "$$m" $$rc; failed=1; fi; \
	done; exit $$failed

check:
	@echo "Run check-mode mutating states per module. Requires live MSAN access."
	@echo "Use: make check ARGS='state=merged config=...'"

check-all: check

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .pytest_cache .coverage
