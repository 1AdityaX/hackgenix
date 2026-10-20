<script lang="ts">
	import { Bell } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Notifications - HackGenix</title>
</svelte:head>

<div class="min-h-screen flex-1 bg-zinc-50 dark:bg-zinc-950">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">Notifications</h1>
			<p class="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
				Stay updated with your latest notifications and alerts
			</p>
		</div>

		<div
			class="rounded-xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
		>
			<div class="text-center">
				<div
					class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800"
				>
					<Bell class="h-8 w-8 text-zinc-400" />
				</div>
				<h3 class="text-lg font-medium text-zinc-900 dark:text-zinc-100">
					No new notifications yet
				</h3>
				<p class="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
					When you receive notifications, they'll appear here
				</p>
			</div>
		</div>
	</div>
</div>
