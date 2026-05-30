.PHONY: test lint compile doc clean setup typecheck coverage check-all gather-all

COLLECTIONS_PATH ?= /tmp/opencode
COLLECTION_LINK := $(COLLECTIONS_PATH)/ansible_collections/nokia/isam
INVENTORY ?= /home/jahknem/Projects/BlueNetworks/yplay-provisioning/inventory/production.yaml
VAULT_PASS ?= /home/jahknem/Projects/BlueNetworks/yplay-provisioning/.vault_pass
TARGET ?= DS-LIN-TEST-01
MODULES := isam_interfaces isam_bridges isam_ethernet_line isam_vlans \
	isam_pon_interfaces isam_ethernet_onts isam_equipment_onts \
	isam_qos_interfaces isam_qos_profiles isam_xdsl_lines isam_xdsl_profiles \
	isam_link_agg isam_xstp isam_equipment

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
	@flake8 plugins/ tests/ --max-line-length=160 --ignore=E501,W503 --statistics || echo "flake8 warnings found"
	@echo "=== ansible-lint ==="
	@ansible-lint plugins/modules/ --quiet || echo "ansible-lint warnings found"

typecheck:
	@echo "=== mypy ==="
	@mypy plugins/module_utils/ plugins/modules/ --ignore-missing-imports --check-untyped-defs || echo "mypy warnings found"

doc:
	@echo "=== ansible-doc validation ==="
	@for m in $(MODULES) isam_facts; do \
		ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) ansible-doc -t module nokia.isam.$$m > /dev/null 2>&1 && \
			echo "  OK nokia.isam.$$m" || echo "  FAIL nokia.isam.$$m"; \
	done

gather-all:
	@for m in $(MODULES) isam_facts; do \
		o=/tmp/opencode/live_$${m}_gathered.out; \
		ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS_PATH) ansible -i $(INVENTORY) $(TARGET) \
			--vault-password-file $(VAULT_PASS) -m nokia.isam.$$m -a 'state=gathered' \
			> $$o 2>&1; \
		rc=$$?; \
		if [ $$rc -eq 0 ]; then printf '  OK %s\n' "$$m"; \
		else printf '  FAIL %s (rc=%s)\n' "$$m" $$rc; fi; \
	done

check-all:
	@echo "Run check-mode mutating states per module. Requires live MSAN access."
	@echo "Use: make check ARGS='state=merged config=...'"

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .pytest_cache .coverage
