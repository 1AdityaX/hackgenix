import type { Handle } from '@sveltejs/kit/hooks';
import { redirect } from '@sveltejs/kit';
import { building } from '$app/env';
import { auth } from '#lib/server/auth.js';
import { svelteKitHandler } from 'better-auth/svelte-kit';

export const handle: Handle = async ({ event, resolve }) => {
	// Let better-auth handle its own routes (/api/auth/*)
	if (event.url.pathname.startsWith('/api/auth')) {
		return svelteKitHandler({ event, resolve, auth, building });
	}

	// Populate session for all other routes
	const session = await auth.api.getSession({
		headers: event.request.headers
	});

	if (session) {
		event.locals.user = {
			id: session.user.id,
			email: session.user.email
		};
	} else {
		event.locals.user = null;
	}

	// Route protection
	const unprotectedRoutes = ['/login', '/signup'];
	const isProtected =
		!unprotectedRoutes.includes(event.url.pathname) && !event.url.pathname.startsWith('/api/');

	if (isProtected && !event.locals.user) {
		redirect(303, '/login');
	}

	if (event.url.pathname === '/login' && event.locals.user) {
		redirect(303, '/');
	}

	return resolve(event);
};
