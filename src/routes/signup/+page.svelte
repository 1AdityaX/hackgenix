<script lang="ts">
	import { authClient } from '#lib/auth-client.js';
	import { goto } from '$app/navigation';

	let name = $state('');
	let email = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function handleSignup(event: Event) {
		event.preventDefault();
		error = null;
		loading = true;

		try {
			const result = await authClient.signUp.email({ name, email, password });
			if (result.error) {
				error = result.error.message || 'Signup failed.';
			} else {
				await goto('/');
			}
		} catch (e: any) {
			error = e.message || 'Signup failed. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<main class="flex h-screen w-full flex-col items-center justify-center bg-gray-50">
	<div
		class="login-box flex min-h-[400px] w-full max-w-[400px] flex-col items-center justify-center rounded-lg border border-gray-200 bg-white p-8 shadow-lg"
	>
		<h1 class="mb-6 text-4xl font-bold text-gray-800">Sign Up</h1>

		<form class="w-full px-4" onsubmit={handleSignup}>
			{#if error}
				<div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
			{/if}

			<div class="mb-4 flex flex-col">
				<label class="mb-1 text-sm font-medium text-gray-700" for="name">Name</label>
				<input
					type="text"
					placeholder="Enter your name"
					id="name"
					name="name"
					required
					bind:value={name}
					class="rounded-md border border-gray-300 p-2 focus:border-violet-500 focus:ring focus:ring-violet-200"
				/>
			</div>

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
					placeholder="Create a password"
					id="password"
					name="password"
					required
					minlength="8"
					bind:value={password}
					class="rounded-md border border-gray-300 p-2 focus:border-violet-500 focus:ring focus:ring-violet-200"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full rounded-lg bg-violet-600 py-2 font-semibold text-white transition duration-200 ease-in-out hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
			>
				{loading ? 'Creating account...' : 'Sign Up'}
			</button>
		</form>

		<p class="mt-6 text-sm text-gray-500">
			Already have an account?
			<a href="/login" class="font-medium text-violet-600 hover:text-violet-700">Login</a>
		</p>
	</div>
</main>
