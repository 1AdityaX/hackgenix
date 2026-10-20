<script lang="ts">
	import favicon from '#lib/assets/favicon.svg';
	import Sidebar from '#lib/components/Sidebar.svelte';
	import { page } from '$app/state';
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="flex min-h-screen bg-zinc-50 dark:bg-zinc-950">
	{#if page.data.user}
		<Sidebar />
	{/if}
	{@render children()}
</div>
