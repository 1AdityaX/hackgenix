<script lang="ts">
	import { authClient } from '#lib/auth-client.js';
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
			const result = await authClient.signIn.email({ email, password });
			if (result.error) {
				error = result.error.message || 'Invalid email or password.';
			} else {
				await goto('/');
			}
		} catch (e: any) {
			error = e.message || 'Login failed. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<main class="flex h-screen w-full flex-col items-center justify-center bg-gray-50">
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

		<p class="mt-6 text-sm text-gray-500">
			Don't have an account?
			<a href="/signup" class="font-medium text-violet-600 hover:text-violet-700">Sign up</a>
		</p>
	</div>
</main>
