import { betterAuth } from 'better-auth';
import { mongodbAdapter } from 'better-auth/adapters/mongodb';
import { BETTER_AUTH_URL } from '$app/env/private';
import { client, db } from './db.js';

export const auth = betterAuth({
	baseURL: BETTER_AUTH_URL,
	database: mongodbAdapter(db, { client }),
	emailAndPassword: {
		enabled: true
	},
	trustedOrigins: [BETTER_AUTH_URL]
});
