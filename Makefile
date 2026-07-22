# NovaOS — common developer targets (Linux build host)

.PHONY: help setup check validate iso vm clean lint

help:
	@echo "NovaOS build targets:"
	@echo "  make validate - static pipeline checks (no root)"
	@echo "  make setup    - install host dependencies (root)"
	@echo "  make check    - validate build host environment"
	@echo "  make iso      - build live ISO (root)"
	@echo "  make vm       - boot latest ISO in QEMU"
	@echo "  make clean    - remove build workdirs"
	@echo "  make lint     - workspace structure check"

validate:
	bash ./scripts/validate-pipeline.sh
	python3 ./tools/lint/validate-static.py

setup:
	sudo bash ./scripts/setup-build-host.sh

check:
	bash ./scripts/check-env.sh

iso:
	sudo bash ./scripts/build-iso.sh

vm:
	bash ./scripts/run-vm.sh

clean:
	bash ./scripts/clean-build.sh --yes

lint:
	bash ./tools/lint/lint-workspace.sh
