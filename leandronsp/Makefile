SHELL = /bin/bash
.ONESHELL:
.DEFAULT_GOAL: help

help: ## Prints available commands
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[.a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

setup: ## First-time setup: dependencies, database, etc
	@bin/setup

dev: ## Start development server
	@bin/dev

server: ## Start Rails server
	@bin/rails server

console: ## Start Rails console
	@bin/rails console

db.create: ## Create databases
	@bin/rails db:create

db.migrate: ## Run migrations
	@bin/rails db:migrate

db.seed: ## Seed database
	@bin/rails db:seed

db.reset: ## Drop, create, migrate, seed
	@bin/rails db:reset

test: ## Run all tests
	@bin/rails test

test.system: ## Run system tests
	@bin/rails test:system

rubocop: ## Run RuboCop linter
	@bin/rubocop

rubocop.fix: ## Auto-correct RuboCop offenses
	@bin/rubocop -a

brakeman: ## Security vulnerability scan
	@bin/brakeman

jobs: ## Start Solid Queue worker
	@bin/jobs

claude.text: ## Run Claude text interaction example
	@ruby main.rb

claude.vision: ## Run Claude vision example
	@ruby main_image.rb
