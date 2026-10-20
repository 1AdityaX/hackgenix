<script lang="ts">
	import eventsData from '#lib/course/events.json';
	import { formatDate, formatTime } from '#lib/format.js';
	import type { CampusEvent } from '#lib/types.js';
	import { Calendar, MapPin } from '@lucide/svelte';

	const events = (eventsData.events as CampusEvent[]).toSorted(
		(a, b) => a.date.localeCompare(b.date) || a.start_time.localeCompare(b.start_time)
	);
</script>

<svelte:head>
	<title>Events - HackGenix</title>
</svelte:head>

<div class="flex h-screen flex-1 flex-col">
	<header
		class="border-b border-zinc-200 bg-white px-4 py-4 shadow-sm sm:px-6 dark:border-zinc-700 dark:bg-zinc-800"
	>
		<h1 class="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">Upcoming Events</h1>
		<p class="text-zinc-600 dark:text-zinc-400">Check out the latest events and happenings</p>
	</header>

	<main class="flex-1 space-y-8 overflow-y-auto p-6">
		{#each events as event (event.event_id)}
			<article
				class="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm transition-all hover:shadow-md sm:p-8 dark:border-zinc-700 dark:bg-zinc-800"
			>
				<h2 class="text-xl font-medium text-zinc-900 dark:text-zinc-100">{event.event_name}</h2>
				<div class="mt-4 space-y-3 text-sm text-zinc-600 dark:text-zinc-300">
					<div class="flex items-center">
						<Calendar class="mr-3 h-4 w-4 shrink-0 text-zinc-500 dark:text-zinc-400" />
						{formatDate(event.date)} • {formatTime(event.start_time)} - {formatTime(event.end_time)}
					</div>
					<div class="flex items-center">
						<MapPin class="mr-3 h-4 w-4 shrink-0 text-zinc-500 dark:text-zinc-400" />
						{event.venue}
					</div>
				</div>
				<p class="mt-4 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">{event.details}</p>
			</article>
		{/each}
	</main>
</div>
