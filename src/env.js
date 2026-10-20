import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	BETTER_AUTH_URL: { schema: (input) => input || 'http://localhost:5173' },
	GOOGLE_CLIENT_ID: {},
	GOOGLE_CLIENT_SECRET: {},
	MONGODB_URI: { schema: (input) => input || 'mongodb://localhost:27017' },
	MONGODB_DB_NAME: { schema: (input) => input || 'hackgenix' }
});
