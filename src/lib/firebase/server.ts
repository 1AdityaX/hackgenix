import { initializeApp, getApp, getApps, type App, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { env } from '$env/dynamic/private';

const serviceAccount = JSON.parse(env.PRIVATE_FIREBASE_SERVICE_ACCOUNT_JSON);

function initializeAdminApp(): App {
	if (getApps().length > 0) {
		return getApp();
	}
	return initializeApp({
		credential: cert({
			projectId: serviceAccount.project_id,
			clientEmail: serviceAccount.client_email,
			privateKey: serviceAccount.private_key
		})
	});
}

export const adminApp = initializeAdminApp();
export const adminAuth = getAuth(adminApp);
