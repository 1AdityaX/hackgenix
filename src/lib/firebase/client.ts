import { initializeApp, type FirebaseApp } from 'firebase/app';
import {
	getAuth,
	onAuthStateChanged,
	GoogleAuthProvider,
	signInWithPopup,
	createUserWithEmailAndPassword,
	signInWithEmailAndPassword,
	signOut as firebaseSignOut,
	type User
} from 'firebase/auth';

import { browser } from '$app/environment';
import {
	PUBLIC_FIREBASE_API_KEY,
	PUBLIC_FIREBASE_AUTH_DOMAIN,
	PUBLIC_FIREBASE_PROJECT_ID,
	PUBLIC_FIREBASE_STORAGE_BUCKET,
	PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
	PUBLIC_FIREBASE_APP_ID
} from '$env/static/public';

import { invalidateAll } from '$app/navigation';

const firebaseConfig = {
	apiKey: PUBLIC_FIREBASE_API_KEY,
	authDomain: PUBLIC_FIREBASE_AUTH_DOMAIN,
	projectId: PUBLIC_FIREBASE_PROJECT_ID,
	storageBucket: PUBLIC_FIREBASE_STORAGE_BUCKET,
	messagingSenderId: PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
	appId: PUBLIC_FIREBASE_APP_ID
};

let currentUser = <User | null>null;
let loading = <boolean>true;
let app: FirebaseApp;
let auth: import('firebase/auth').Auth;

function initializeFirebase() {
	if (!browser) return;
	app = initializeApp(firebaseConfig);
	auth = getAuth(app);

	onAuthStateChanged(auth, async (user) => {
		currentUser = user;
		if (user) {
			const token = await user.getIdToken();
			try {
				const response = await fetch('/api/auth/session', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ token })
				});
				if (!response.ok) {
					console.error('Failed to set session cookie:', response.status, await response.text());
				}
				await invalidateAll();
			} catch (error) {
				console.error('Error fetching session API:', error);
			}
		}
		loading = false;
	});
}

async function signInWithGoogle() {
	const provider = new GoogleAuthProvider();
	await signInWithPopup(auth, provider);
}

async function signOut() {
	await firebaseSignOut(auth);
	// Clear the session cookie by calling our server endpoint
	await fetch('/api/auth/session', { method: 'DELETE' });
}

export const authState = {
	get user() {
		return currentUser;
	},
	get loading() {
		return loading;
	}
};

export {
	initializeFirebase,
	signInWithGoogle,
	createUserWithEmailAndPassword,
	signInWithEmailAndPassword,
	signOut,
	auth
};
