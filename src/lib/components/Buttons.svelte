<script>
	let { name, icon = null, href = '' } = $props();
	const StartingIcon = icon;
</script>

{#if href}
	<a
		{href}
		class="flex w-full items-center overflow-hidden bg-inherit px-5 py-2 text-base text-zinc-900 hover:bg-zinc-300 dark:text-zinc-100 dark:hover:bg-zinc-700"
	>
		{#if StartingIcon}
			<StartingIcon class="mr-2 inline-block h-5 w-5" />
		{/if}
		<span class="truncate whitespace-nowrap">{name}</span>
	</a>
{:else}
	<button
		class="flex w-full items-center overflow-hidden bg-inherit px-5 py-2 text-base text-zinc-900 hover:bg-zinc-300 dark:text-zinc-100 dark:hover:bg-zinc-700"
		type="button"
		disabled
	>
		{#if StartingIcon}
			<StartingIcon class="mr-2 inline-block h-5 w-5" />
		{/if}
		<span class="truncate whitespace-nowrap">{name}</span>
	</button>
{/if}
