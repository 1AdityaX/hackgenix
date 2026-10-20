<script lang="ts">
	import { Bell, Calendar, House, NotepadText, PartyPopper } from '@lucide/svelte';

	const links = [
		{ name: 'My Workspace', icon: House, href: '/' },
		{ name: 'Notifications', icon: Bell, href: '/notifications' },
		{ name: 'Todo', icon: NotepadText, href: '/todo' },
		{ name: 'Schedule', icon: Calendar, href: '/schedule' },
		{ name: 'Events', icon: PartyPopper, href: '/events' }
	];
</script>

<aside class="flex min-h-screen w-60 flex-col gap-2 bg-zinc-200 pt-5 dark:bg-zinc-900">
	{#each links as { name, icon: Icon, href }}
		<a
			{href}
			class="flex items-center px-5 py-2 text-base text-zinc-900 hover:bg-zinc-300 dark:text-zinc-100 dark:hover:bg-zinc-700"
		>
			<Icon class="mr-2 h-5 w-5" />
			<span class="truncate">{name}</span>
		</a>
	{/each}
</aside>
