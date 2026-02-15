# HackGenix - Student Life Dashboard

A student life management dashboard built with SvelteKit, featuring AI-powered assistance, task management, schedule viewing, and event tracking.

## Tech Stack

**Frontend**
- SvelteKit 2 + Svelte 5 (runes)
- Tailwind CSS 4
- TypeScript
- Lucide icons

**Authentication**
- [better-auth](https://www.better-auth.com/) (email/password + Google OAuth)

**Database**
- MongoDB

**AI Backend**
- Python FastAPI server
- Google Gemini 2.0 Flash with function calling (agentic RAG)

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (recommended) or MongoDB installed locally
- Google Gemini API key
- Google OAuth credentials (for Google sign-in)

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd hackgenix
npm install
```

### 2. Configure environment variables

Copy the example env files and fill in your values:

```bash
cp .env.example .env
cp server/.env.example server/.env
```

**`.env`** (SvelteKit):

| Variable | Description |
|----------|-------------|
| `BETTER_AUTH_SECRET` | Random secret, min 32 chars. Generate with `openssl rand -base64 32` |
| `BETTER_AUTH_URL` | Your app URL (`http://localhost:5173` for dev) |
| `VITE_BETTER_AUTH_URL` | Same as above (exposed to client) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `MONGODB_URI` | MongoDB connection string (`mongodb://localhost:27017`) |
| `MONGODB_DB_NAME` | Database name (`hackgenix`) |
| `PRIVATE_RAG_SERVER_URL` | Python backend URL (`http://localhost:8000`) |

**`server/.env`** (Python backend):

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `MONGODB_URI` | Same MongoDB URI as above |
| `MONGODB_DB_NAME` | Same database name as above |
| `CORS_ORIGINS` | Allowed origins (default: `http://localhost:5173,http://localhost:4173`) |

### 3. Set up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `http://localhost:5173/api/auth/callback/google`
4. Copy the Client ID and Client Secret to your `.env`

### 4. Start MongoDB

**Option A: Docker Compose (recommended)**

```bash
docker compose up -d
```

This starts a MongoDB 7 container on port 27017 with persistent volume storage.

**Option B: Homebrew (macOS)**

```bash
brew services start mongodb-community
```

**Option C: System service (Linux)**

```bash
sudo systemctl start mongod
```

### 5. Set up the database

**For local development** (creates collections, indexes, and mock data):

```bash
mongosh mongodb://localhost:27017/hackgenix scripts/db-setup-local.js
```

Or if using Docker:

```bash
docker exec -i hackgenix-mongo mongosh hackgenix < scripts/db-setup-local.js
```

This creates a test account you can use immediately:
- **Email:** `student@hackgenix.dev`
- **Password:** `password123`

**For production** (creates collections and indexes only, no data):

```bash
mongosh "mongodb+srv://user:pass@your-cluster.mongodb.net/hackgenix" scripts/db-setup-prod.js
```

### 6. Set up the Python backend

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

Start both the SvelteKit frontend and Python backend:

```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Python backend
cd server
source venv/bin/activate
python agentic_rag.py
```

The app will be available at `http://localhost:5173`.

## Database

### Collections

| Collection | Purpose |
|------------|---------|
| `user` | User profiles (managed by better-auth) |
| `session` | Active sessions with TTL expiry (managed by better-auth) |
| `account` | Auth provider credentials — email/password, Google OAuth (managed by better-auth) |
| `verification` | Email verification tokens with TTL (managed by better-auth) |
| `todos` | User tasks (managed by the app) |

### Scripts

| Script | What it does |
|--------|-------------|
| `scripts/db-setup-local.js` | Drops & recreates all collections, creates indexes, inserts a mock user and sample todos |
| `scripts/db-setup-prod.js` | Creates collections and indexes if they don't exist. Inserts nothing. Safe to re-run. |

## Project Structure

```
hackgenix/
├── src/
│   ├── lib/
│   │   ├── server/
│   │   │   ├── auth.ts          # better-auth server config
│   │   │   └── db.ts            # MongoDB connection
│   │   ├── components/          # Svelte components
│   │   ├── course/              # JSON data (timetable, events, courses)
│   │   ├── auth-client.ts       # better-auth client
│   │   └── types.ts             # TypeScript interfaces
│   ├── routes/
│   │   ├── +page.svelte         # Dashboard
│   │   ├── login/               # Login page
│   │   ├── signup/              # Signup page
│   │   ├── todo/                # Todo management
│   │   ├── events/              # Events listing
│   │   ├── schedule/            # Timetable view
│   │   ├── chatai/              # AI assistant
│   │   └── api/
│   │       ├── todos/           # Todo CRUD API
│   │       └── chat/            # Chat proxy to Python backend
│   └── hooks.server.ts          # Auth middleware
├── server/
│   ├── agentic_rag.py           # FastAPI + Gemini RAG server
│   └── requirements.txt         # Python dependencies
├── scripts/
│   ├── db-setup-local.js        # Local dev DB setup (schema + mock data)
│   └── db-setup-prod.js         # Production DB setup (schema only)
├── docker-compose.yml           # MongoDB container
└── static/                      # Static assets
```

## Features

- **Authentication**: Email/password and Google OAuth via better-auth
- **Todo Management**: Create, complete, and delete tasks
- **Schedule**: View your timetable by day and batch
- **Events**: Browse upcoming university events
- **AI Assistant**: Chat with an AI that can access your schedule, todos, and campus data
- **Dark Mode**: Full dark theme support

## Scripts

```bash
npm run dev       # Start dev server
npm run build     # Production build
npm run preview   # Preview production build
npm run check     # TypeScript checking
npm run format    # Format code with Prettier
```
