# Macedo

Rails 8.0.3 application with Anthropic Claude AI integration.

## Tech Stack

- Ruby 3.4.4
- Rails 8.0.3
- SQLite3 with Solid adapters
- Hotwire (Turbo + Stimulus)

## Setup

```bash
make setup
```

## Authentication

The app uses Devise for user authentication. After running seeds, you can login with:

**Test Users:**
- Email: `alice@macedo.com` | Senha: `senha123`
- Email: `bob@macedo.com` | Senha: `senha123`
- Email: `carol@macedo.com` | Senha: `senha123`

Each user has 3 dishes with AI-generated descriptions and pairing suggestions.

**Features:**
- User registration and login
- Password recovery
- Isolated dishes per user
- Automatic dish analysis with Claude AI on upload

## Development

```bash
make dev          # Start server
make jobs         # Start background job worker (required for AI analysis)
make console      # Rails console
make test         # Run tests
```

**Note**: For AI dish analysis to work, you need to run **two processes**:
1. Rails server: `make dev` (or `bin/dev`)
2. Job worker: `make jobs` (or `bin/jobs`)

The job worker processes background tasks like Claude AI analysis.

## Database

```bash
make db.migrate   # Run migrations
make db.reset     # Reset database
```

## Code Quality

```bash
make rubocop      # Lint
make rubocop.fix  # Auto-fix
make brakeman     # Security scan
```

## Claude API Integration

The app integrates Claude AI for dish image analysis and pairing suggestions.

### Architecture

**Background Jobs (Solid Queue)**:
- All Claude API calls run asynchronously via `AnalyzeDishJob`
- Dishes are created instantly with placeholder text
- AI analysis happens in the background (5-10 seconds)
- Users can refresh the page to see results

**Services**:
- **Claude::Client** - Wrapper around ruby-anthropic with retry logic
- **Claude::Analyzer** - Dish analysis with Brazilian easter eggs
- **Claude::ProfileAnalyzer** - User eating pattern analysis
- **Claude::Config** - Centralized configuration

**Jobs**:
- **AnalyzeDishJob** - Background job for dish image analysis with retry logic

### Configuration

```env
ANTHROPIC_API_KEY=sk-ant-...        # Required
CLAUDE_MODEL=claude-sonnet-4-5-20250929
MAX_TOKENS=4096
TEMPERATURE=1.0
MACEDO_MOOD=philosophical           # Easter egg mode
```

### Usage

```ruby
# Simple chat
client = Claude::Client.new
response = client.chat("Tell me about wine pairing")

# Dish analysis (runs automatically via background job on image upload)
analyzer = Claude::Analyzer.new(dish.image)
result = analyzer.analyze
# Returns: { dish_name:, description:, pairing_suggestions:, ... }

# User profile analysis
analyzer = Claude::ProfileAnalyzer.new(user)
profile = analyzer.analyze
# Returns: "Explorador gastronômico que não tem medo de experimentar"

# Manual background job enqueue
AnalyzeDishJob.perform_later(dish.id)
UpdateUserProfilesJob.perform_now
```

### Standalone Examples

```bash
make claude.text    # Text interaction
make claude.vision  # Vision/image analysis
```

## Commands

Run `make` to see all available commands.
