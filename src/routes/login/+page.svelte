<script lang="ts">
	import { signInWithGoogle, auth, signInWithEmailAndPassword } from '$lib/firebase/client';
	import { goto } from '$app/navigation';

	let email = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function handleEmailPasswordLogin(event: Event) {
		event.preventDefault();
		error = null;
		loading = true;

		try {
			await signInWithEmailAndPassword(auth, email, password);
			await goto('/');
		} catch (e: any) {
			if (
				e.code === 'auth/invalid-credential' ||
				e.code === 'auth/user-not-found' ||
				e.code === 'auth/wrong-password'
			) {
				error = 'Invalid email or password. Please try again.';
			} else if (e.code === 'auth/too-many-requests') {
				error = 'Too many failed login attempts. Please try again later.';
			} else {
				error = e.message || 'Login failed. Please try again.';
			}
			console.error('Login error:', e);
		} finally {
			loading = false;
		}
	}

	async function handleGoogleLogin() {
		error = null;
		loading = true;
		try {
			await signInWithGoogle();
			await goto('/');
		} catch (e: any) {
			error = e.message;
			console.error('Google login error:', e);
		} finally {
			loading = false;
		}
	}
</script>

<main class="flex w-full h-screen flex-col items-center justify-center bg-gray-50">
	<div
		class="login-box flex min-h-[400px] w-full max-w-[400px] flex-col items-center justify-center rounded-lg border border-gray-200 bg-white p-8 shadow-lg"
	>
		<h1 class="mb-6 text-4xl font-bold text-gray-800">Login</h1>

		<form class="w-full px-4" onsubmit={handleEmailPasswordLogin}>
			{#if error}
				<div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
			{/if}

			<div class="mb-4 flex flex-col">
				<label class="mb-1 text-sm font-medium text-gray-700" for="email">Email</label>
				<input
					type="email"
					placeholder="Enter your email"
					id="email"
					name="email"
					required
					bind:value={email}
					class="rounded-md border border-gray-300 p-2 focus:border-violet-500 focus:ring focus:ring-violet-200"
				/>
			</div>

			<div class="mb-6 flex flex-col">
				<label class="mb-1 text-sm font-medium text-gray-700" for="password">Password</label>
				<input
					type="password"
					placeholder="Enter your password"
					id="password"
					name="password"
					required
					bind:value={password}
					class="rounded-md border border-gray-300 p-2 focus:border-violet-500 focus:ring focus:ring-violet-200"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full rounded-lg bg-violet-600 py-2 font-semibold text-white transition duration-200 ease-in-out hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
			>
				{loading ? 'Logging in...' : 'Login'}
			</button>
		</form>

		<div class="relative my-6 flex w-full items-center px-4">
			<div class="flex-grow border-t border-gray-300"></div>
			<span class="mx-4 flex-shrink text-gray-500">or</span>
			<div class="flex-grow border-t border-gray-300"></div>
		</div>

		<div class="w-full px-4">
			<button
				onclick={handleGoogleLogin}
				type="button"
				disabled={loading}
				class="flex w-full items-center justify-center rounded-lg border border-gray-300 bg-white py-2 font-semibold text-gray-700 shadow-sm transition duration-200 ease-in-out hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
			>
				<img src="google_logo.svg" alt="Google logo" class="mr-2 h-5 w-5" />
				{loading ? 'Logging in...' : 'Login with Google'}
			</button>
		</div>
	</div>
</main>
