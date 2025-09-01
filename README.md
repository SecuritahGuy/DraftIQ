# DraftIQ

A local Fantasy Football analytics platform that integrates with Yahoo Fantasy Football API to provide comprehensive fantasy football management tools.

## Features

- **Start/Sit Assistant** with one-click lineup submission
- **Waiver Wire Assistant** with FAAB guidance
- **Trade Analyzer** with league-wide analysis
- **Draft Tools** with league-aware mock drafts
- **Auto-Pilot** for automated lineup management

## Technology Stack

- **Backend**: FastAPI with SQLAlchemy 2.0 and SQLite
- **Data Sources**: Yahoo Fantasy API, nfl_data_py for NFL statistics
- **Authentication**: OAuth 2.0 with Yahoo
- **Data Processing**: Python with pandas, numpy for analytics
- **Testing**: pytest with async support

## Development Setup

### Cursor Rules

This project includes comprehensive cursor rules to guide AI assistants in providing consistent, high-quality code suggestions:

- **`.cursor/rules/`** - Modern cursor rules format with metadata and scoping
  - `draftiq-project.mdc` - Main project-wide guidelines
  - `fastapi-development.mdc` - FastAPI development patterns
  - `yahoo-api-integration.mdc` - Yahoo Fantasy API integration
  - `nfl-data-processing.mdc` - NFL data processing with nfl_data_py
  - `fantasy-analytics.mdc` - Fantasy football analytics and recommendations

The cursor rules follow the modern `.cursor/rules/` format with proper metadata, glob patterns, and scoping for different file types and domains.

### Getting Started

1. Clone the repository
2. Install dependencies: `pip install fastapi uvicorn sqlalchemy aiosqlite pydantic-settings python-dotenv`
3. Set up environment variables (see `env.example`)
4. Run the development server: `python -m uvicorn app.main:app --reload`

### Current Status

✅ **Phase 1 - Step 1 Complete**: FastAPI app + SQLite (SQLAlchemy 2.0)
- Basic FastAPI application structure
- SQLAlchemy 2.0 async database setup
- SQLite database with connection pooling
- Configuration management with Pydantic Settings
- Health check and root endpoints
- Auto-generated API documentation at `/docs`

✅ **Phase 1 - Step 2 Complete**: OAuth flow with Yahoo (3-legged)
- Yahoo OAuth service with authorization URL generation
- OAuth callback endpoint for token exchange
- User and YahooToken models for database storage
- Pydantic schemas for OAuth requests/responses
- OAuth state management for security
- Direct authorization redirect endpoint

⏳ **Phase 1 - Step 3 Pending**: Initial sync endpoints
- `/yahoo/leagues` – list user's leagues
- `/yahoo/league/{league_key}/pull` – scoring, rosters, draft results, schedule, transactions
- `/yahoo/team/{team_key}/roster?week=` – current roster snapshot; cache weekly

## Project Structure

```
draftiq/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI app entry point
│   ├── core/              # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py      # Settings and environment
│   │   └── database.py    # Database connection
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   └── v1/            # API version 1
│   │       ├── __init__.py
│   │       └── auth.py    # OAuth authentication endpoints
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py        # Base model class
│   │   └── user.py        # User and OAuth token models
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py
│   │   └── auth.py        # Authentication schemas
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   └── yahoo_oauth.py # Yahoo OAuth service
│   ├── utils/             # Utility functions
│   │   └── __init__.py
│   └── tests/             # Test files
│       └── __init__.py
├── .cursor/               # Cursor rules (modern format)
│   └── rules/             # AI assistant guidelines
├── draftiq.db            # SQLite database
├── env.example           # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Contributing

Please read the cursor rules and follow the established patterns for consistent code quality. See the roadmap for detailed development plans.

## License

See [LICENSE](LICENSE) for details.