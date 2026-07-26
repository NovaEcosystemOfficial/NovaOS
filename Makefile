# NovaOS — common developer targets (Linux build host)

.PHONY: help setup check validate validate-update test-update iso vm smoke verify-desktop p0-gate install-gate validate-installer clean lint

help:
	@echo "NovaOS build targets:"
	@echo "  make validate            - static pipeline checks (no root)"
	@echo "  make validate-update     - Nova Update foundation smoke (no root)"
	@echo "  make test-update         - local RPM repo e2e (check→apply, no ISO)"
	@echo "  make validate-installer  - static Calamares installer checks (no root)"
	@echo "  make setup               - install host dependencies (root)"
	@echo "  make check               - validate build host environment"
	@echo "  make iso                 - build live+installable ISO (root)"
	@echo "  make smoke               - headless QEMU desktop smoke (virtio+qxl)"
	@echo "  make verify-desktop      - build ISO + automated desktop smoke"
	@echo "  make p0-gate             - Foundation live P0 stability gate (root)"
	@echo "  make install-gate        - installer presence gate on ISO (root)"
	@echo "  make vm                  - boot latest ISO in QEMU"
	@echo "  make clean               - remove build workdirs"
	@echo "  make lint                - workspace structure check"

validate:
	bash ./scripts/validate-pipeline.sh
	python3 ./tools/lint/validate-static.py
	bash ./scripts/validate-installer.sh
	bash ./scripts/validate-update.sh

validate-update:
	bash ./scripts/validate-update.sh

test-update:
	bash ./scripts/update-test/run-e2e-update-flow.sh

validate-installer:
	bash ./scripts/validate-installer.sh

setup:
	sudo bash ./scripts/setup-build-host.sh

check:
	bash ./scripts/check-env.sh

iso:
	sudo bash ./scripts/build-iso.sh

smoke:
	bash ./scripts/smoke-desktop.sh

verify-desktop:
	sudo bash ./scripts/build-and-verify-desktop.sh

p0-gate:
	sudo bash ./scripts/qa-p0-gate.sh

install-gate:
	sudo bash ./scripts/qa-install-gate.sh

vm:
	bash ./scripts/run-vm.sh

clean:
	bash ./scripts/clean-build.sh --yes

lint:
	bash ./tools/lint/lint-workspace.sh
