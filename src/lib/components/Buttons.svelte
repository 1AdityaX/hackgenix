<script>
	import { goto } from '$app/navigation';
	let { name, icon = null, href = '' } = $props();
	const StartingIcon = icon;

	function handleClick() {
		if (!href) return;
		goto(href);
	}
</script>

<button
	class="flex w-full items-center overflow-hidden bg-inherit px-5 py-2 text-base text-zinc-900 hover:bg-zinc-300 dark:text-zinc-100 dark:hover:bg-zinc-700"
	onclick={handleClick}
>
	{#if StartingIcon}
		<StartingIcon class="mr-2 inline-block h-5 w-5" />
	{/if}
	<span class="truncate whitespace-nowrap">{name}</span>
</button>
