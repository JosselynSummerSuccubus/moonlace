.PHONY: run recent recent-open
DATE ?= $(shell date +%F)

run:
	@python moonlace.py -p ollama -d "$(DATE)" -q "$(Q)"

recent:
	@python3 ~/code/stellarwind/tools/list_recent.py "$(DATE)"

recent-open:
	@files=$$(python3 ~/code/stellarwind/tools/list_recent.py "$(DATE)" | awk '{print $$NF}'); \
	kate -n $$(for f in $$files; do printf "data/derived/%s/%s " "$(DATE)" "$$f"; done)
