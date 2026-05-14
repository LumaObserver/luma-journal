Curiosity Pulse (dry-run)

This folder contains templates and scripts for the Curiosity Pulse feature.

Usage (dry-run):
- Run the generator: ./ops/curiosity_run.sh
- It will create a sample pulse in curiosity/outbox/*.md (dry-run mode). Do not enable Telegram sends until tone is approved.

Files tracked in git:
- templates/prompts.md
- ops/curiosity_prompt.py
- ops/curiosity_run.sh
- README.md

Files intentionally untracked (added to .gitignore):
- curiosity/outbox/
- curiosity/sent/
- curiosity/failed/
- curiosity/state.json
- logs/curiosity.log
