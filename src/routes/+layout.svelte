<script lang="ts">
	import Sidebar from "$lib/components/Sidebar.svelte";
	import { initializeFirebase, authState, signOut } from '$lib/firebase/client';
	import { goto } from '$app/navigation';
	import '../app.css';
	import { setContext } from 'svelte';

	let { children } = $props();

	$effect.pre(() => {
		initializeFirebase();
	});

	function handleSignOut() {
		signOut().then(() => {
			goto('/login');
		});
	}

	setContext('auth', {
		authState,
		handleSignOut
	});
</script>

<main>
    <div class="bg-zinc-50 dark:bg-zinc-950 min-h-screen flex">
        <aside>
            <Sidebar />
        </aside>
		{@render children()}
    </div>
</main>


