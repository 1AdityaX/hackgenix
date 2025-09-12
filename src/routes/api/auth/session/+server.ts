import { adminAuth } from '$lib/firebase/server';
import { json, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { token } = await request.json();
	if (!token) {
		return json({ status: 'error', message: 'No token provided.' }, { status: 400 });
	}
	const expiresIn = 60 * 60 * 24 * 5 * 1000; // 5 days

	try {
		const sessionCookie = await adminAuth.createSessionCookie(token, { expiresIn });
		cookies.set('session', sessionCookie, {
			path: '/',
			httpOnly: true,
			secure: true,
			maxAge: expiresIn / 1000
		});
		return json({ status: 'signedIn' });
	} catch (error) {
		console.error('Session cookie error:', error);
		return json({ status: 'error', message: 'Could not create session.' }, { status: 401 });
	}
};

export const DELETE: RequestHandler = async ({ cookies }) => {
	cookies.delete('session', { path: '/' });
	return json({ status: 'signedOut' });
};
