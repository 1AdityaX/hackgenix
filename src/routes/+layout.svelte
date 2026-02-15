<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { authClient } from '$lib/auth-client';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import '../app.css';
	import { setContext } from 'svelte';

	let { children } = $props();

	function handleSignOut() {
		authClient.signOut().then(() => {
			goto('/login');
		});
	}

	setContext('auth', {
		handleSignOut
	});

	// Check if current page is login page
	let isLoginPage = $derived(page.route.id === '/login');
</script>

<main>
	<div class="flex min-h-screen bg-zinc-50 dark:bg-zinc-950">
		{#if !isLoginPage}
			<aside>
				<Sidebar />
			</aside>
		{/if}
		{@render children()}
	</div>
</main>
