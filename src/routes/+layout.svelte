<script lang="ts">
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

{@render children()}

