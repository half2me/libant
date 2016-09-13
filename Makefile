init:
    python3 setup.py install

test:
    py.test tests

.PHONY: init test