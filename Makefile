PY_TARGETS := qemu-raspi parse-config-txt src/qemu_raspi/*.py
SH_TARGETS := build-qemu run-qemu

checks: isort ruff-check ruff-format shellcheck

dtmerge: src/dtmerge/dtmerge

src/dtmerge/dtmerge:
	cmake -S src/dtmerge -B src/dtmerge
	make -C src/dtmerge

clean:
	make -C src/dtmerge clean
	rm -f src/dtmerge/CMakeCache.txt

isort:
	isort $(PY_TARGETS)

ruff-check:
	pyvenv ruff check $(PY_TARGETS)

ruff-format:
	pyvenv ruff format --line-length=120 $(PY_TARGETS)

shellcheck:
	shellcheck $(SH_TARGETS)
