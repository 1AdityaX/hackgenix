<script>
	let { name, icon = null } = $props();
	const StartingIcon = icon;
</script>

<button
	class="flex w-full items-center bg-inherit px-5 py-2 text-base text-zinc-900 hover:bg-zinc-300 dark:text-zinc-100 dark:hover:bg-zinc-700 overflow-hidden"
>
	{#if StartingIcon}
		<StartingIcon class="mr-2 inline-block h-5 w-5" />
	{/if}
	<span class="truncate whitespace-nowrap">{name}</span>
</button>