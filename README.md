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
2. Set up Python environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up frontend dependencies:
   ```bash
   cd web
   npm install
   cd ..
   ```
4. Set up environment variables (see `env.example`)
5. Start development servers:
   ```bash
   # Option 1: Use the startup script (recommended)
   ./start-dev.sh  # On Windows: start-dev.bat
   
   # Option 2: Start manually
   # Terminal 1: Backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   # Terminal 2: Frontend
   cd web && npm run dev
   ```

### Development URLs

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

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

✅ **Phase 1 Complete**: All three steps completed
- FastAPI app + SQLite (SQLAlchemy 2.0)
- OAuth flow with Yahoo (3-legged)
- Initial sync endpoints for leagues, teams, and rosters

✅ **Phase 2 Complete**: Data model (SQLite first)
- Core database tables for leagues, teams, players, rosters, and NFL data
- Data synchronization service with caching strategies
- Player ID mapping between Yahoo and public data sources (nfl_data_py)
- Comprehensive API endpoints for data sync and player mapping
- NFL data import functionality working (12,114 players processed)

✅ **Phase 3 Complete**: Scoring engine & projections
- NFL data ingestion service with comprehensive API endpoints
- Custom scoring compiler for Yahoo league rules with tier-based and threshold scoring
- Usage-driven baseline projections using depth charts, snap shares, and recent performance
- Position-specific projection models (QB, RB, WR, TE, K) with injury adjustments
- CSV import/export functionality for custom projections
- Fantasy points calculator with detailed breakdowns

🔄 **Phase 3.5 In Progress**: React Web UI
- Fast, local-first UI for actionable insights
- Connect → Dashboard → Weekly Lineup workflow
- Integration with all backend services

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
│   │       ├── auth.py    # OAuth authentication endpoints
│   │       ├── yahoo.py   # Yahoo sync endpoints
│   │       ├── data_sync.py # Data sync and mapping endpoints
│   │       ├── nfl_data.py # NFL data ingestion endpoints
│   │       ├── scoring.py # Fantasy scoring endpoints
│   │       ├── projections.py # Projection generation endpoints
│   │       └── csv_import.py # CSV import/export endpoints
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py        # Base model class
│   │   ├── user.py        # User and OAuth token models
│   │   ├── fantasy.py     # Fantasy football models
│   │   └── nfl_data.py    # NFL data models (stats, projections, injuries)
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication schemas
│   │   ├── yahoo.py       # Yahoo API schemas
│   │   └── nfl_data.py    # NFL data schemas
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── yahoo_oauth.py # Yahoo OAuth service
│   │   ├── yahoo_api.py   # Yahoo API client service
│   │   ├── data_sync.py   # Data synchronization service
│   │   ├── player_mapping.py # Player ID mapping service
│   │   ├── nfl_data_ingestion.py # NFL data ingestion service
│   │   ├── scoring_engine.py # Fantasy scoring engine
│   │   ├── projection_engine.py # Projection generation engine
│   │   └── csv_import.py # CSV import/export service
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