# Makefile for the RPAL parser

# Specify the Python interpreter
PYTHON = python3

# Specify the source file
SRC_FILE = myrpal.py

all:
	$(PYTHON) $(SRC_FILE) -ast $(RPAL_FILE)

clean:
	rm -f output.txt

help:
	@echo "Available targets:"
	@echo "  all: Run the Python script and generate the output file"
	@echo "  clean: Remove the output file"
	@echo "  help: Display this help message"

.PHONY: all clean help
