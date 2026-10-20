# HackGenix - Student Life Dashboard

A student dashboard built with SvelteKit: todos, class timetable, and campus events, behind email/password or Google sign-in.

## Tech stack

- SvelteKit 3, Svelte 5, Vite 8, Tailwind CSS 4, TypeScript
- [better-auth](https://www.better-auth.com/) for authentication
- MongoDB

## Prerequisites

- Node.js 22.17+ (see `.nvmrc`)
- MongoDB, via Docker Compose or a local install
- Google OAuth credentials (only for Google sign-in)

## Setup

```bash
npm install
cp .env.example .env   # then fill in the values
docker compose up -d   # starts MongoDB 8 on port 27017
mongosh mongodb://localhost:27017/hackgenix scripts/db-setup.js
npm run dev
```

The app runs at `http://localhost:5173`. Create an account on the sign-up page.

### Environment variables

| Variable               | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| `BETTER_AUTH_SECRET`   | Random secret, min 32 chars. Generate with `openssl rand -base64 32` |
| `BETTER_AUTH_URL`      | App URL (`http://localhost:5173` in dev)                             |
| `VITE_BETTER_AUTH_URL` | Same value, exposed to the browser                                   |
| `GOOGLE_CLIENT_ID`     | Google OAuth client ID                                               |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret                                           |
| `MONGODB_URI`          | MongoDB connection string (default `mongodb://localhost:27017`)      |
| `MONGODB_DB_NAME`      | Database name (default `hackgenix`)                                  |

Server-side variables are declared in `src/env.js` and imported from `$app/env/private`.

### Google OAuth

1. Create OAuth 2.0 credentials in the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Add `http://localhost:5173/api/auth/callback/google` as an authorized redirect URI.
3. Put the client ID and secret in `.env`.

## Database

`scripts/db-setup.js` creates the indexes the app relies on and is safe to re-run against any environment. With Docker:

```bash
docker exec -i hackgenix-mongo mongosh hackgenix < scripts/db-setup.js
```

| Collection                                   | Purpose                |
| -------------------------------------------- | ---------------------- |
| `user`, `session`, `account`, `verification` | Managed by better-auth |
| `todos`                                      | User tasks             |

## Timetable data

The schedule page reads `src/lib/course/timetable.json` and `studentCourse.json`. To regenerate the timetable from the CSV exports in `scripts/data/`:

```bash
python3 scripts/parse_csv_timetable.py
```

## Project structure

```
src/
├── env.js                 # server env var declarations
├── hooks.server.ts        # session lookup and route protection
├── lib/
│   ├── auth-client.ts     # better-auth browser client
│   ├── server/            # better-auth config, MongoDB client
│   ├── components/        # Sidebar
│   ├── course/            # timetable, courses, events JSON
│   ├── format.ts          # date/time formatting
│   └── types.ts
└── routes/
    ├── +page.svelte       # dashboard
    ├── login/, signup/
    ├── todo/, schedule/, events/, notifications/
    └── api/todos/         # todo CRUD
```

## Scripts

```bash
npm run dev       # dev server
npm run build     # production build
npm run preview   # preview the build
npm run check     # type-check
npm run format    # format with Prettier
npm run lint      # check formatting
```

## Updating dependencies

Dependabot opens weekly PRs for npm packages and monthly ones for the Mongo image. Manually: `npm outdated`, `npm update`, and `npx sv migrate <migration>` for SvelteKit or Svelte majors. SvelteKit is configured in `vite.config.js`; there is no `svelte.config.js` since SvelteKit 3.
