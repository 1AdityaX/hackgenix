import { adminAuth } from '$lib/firebase/server';
import type { Handle } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	const sessionCookie = event.cookies.get('session');

	try {
		const decodedClaims = await adminAuth.verifySessionCookie(sessionCookie!, true);
		event.locals.user = {
			uid: decodedClaims.uid,
			email: decodedClaims.email || null
		};
	} catch (e) {
		event.locals.user = null;
		if (sessionCookie) {
			event.cookies.delete('session', { path: '/' });
		}
	}
	const unprotectedRoutes = ['/login', '/signup', '/api/auth/session'];

	const isProtected = !unprotectedRoutes.includes(event.url.pathname);

	if (isProtected && !event.locals.user) {
		redirect(303, '/login');
	}

	if (!isProtected && event.locals.user) {
		redirect(303, '/');
	}

	return resolve(event);
};
