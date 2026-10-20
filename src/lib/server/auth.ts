import { betterAuth } from 'better-auth';
import { mongodbAdapter } from 'better-auth/adapters/mongodb';
import { BETTER_AUTH_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET } from '$app/env/private';
import { client, db } from './db.js';

export const auth = betterAuth({
	baseURL: BETTER_AUTH_URL,
	database: mongodbAdapter(db, { client }),
	emailAndPassword: {
		enabled: true
	},
	socialProviders: {
		google: {
			clientId: GOOGLE_CLIENT_ID,
			clientSecret: GOOGLE_CLIENT_SECRET
		}
	},
	trustedOrigins: [BETTER_AUTH_URL]
});
