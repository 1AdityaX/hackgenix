<script lang="ts">
	import eventsData from '$lib/course/events.json';
	import type { Event } from '$lib/types';

	const events: Event[] = eventsData.events;

	// Format date to be more readable (e.g., "2025-10-15" -> "Oct 15, 2025")
	function formatDate(dateString: string): string {
		const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
		return new Date(dateString).toLocaleDateString('en-US', options);
	}

	// Format time to 12-hour format with AM/PM
	function formatTime(timeString: string): string {
		const [hours, minutes] = timeString.split(':');
		const hour = parseInt(hours, 10);
		const ampm = hour >= 12 ? 'PM' : 'AM';
		const hour12 = hour % 12 || 12;
		return `${hour12}:${minutes} ${ampm}`;
	}

	// Sort events by date and then by start time
	const sortedEvents = [...events].sort((a, b) => {
		const dateCompare = new Date(a.date).getTime() - new Date(b.date).getTime();
		if (dateCompare !== 0) return dateCompare;
		return a.start_time.localeCompare(b.start_time);
	});
</script>

<div class="flex h-screen w-full flex-col">
	<header
		class="w-full border-b border-zinc-200 bg-white px-4 py-4 shadow-sm sm:px-6 dark:border-zinc-700 dark:bg-zinc-800"
	>
		<div class="mx-auto w-full max-w-[calc(100%-16rem)]">
			<h1 class="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">Upcoming Events</h1>
			<p class="text-zinc-600 dark:text-zinc-400">Check out the latest events and happenings</p>
		</div>
	</header>

	<main class="flex-1 overflow-hidden">
		<div class="mx-auto h-full w-full max-w-[calc(100%-16rem)] overflow-y-auto p-6">
			<div class="space-y-8">
				{#each sortedEvents as event}
					<article
						class="overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-zinc-700 dark:bg-zinc-800"
					>
						<div class="p-6 sm:p-8">
							<div class="flex flex-col sm:flex-row sm:items-start sm:justify-between">
								<div class="flex-1">
									<h2 class="text-xl font-medium text-zinc-900 dark:text-zinc-100">
										{event.event_name}
									</h2>
									<div class="mt-4 space-y-3 text-sm text-zinc-600 dark:text-zinc-300">
										<div class="flex items-center">
											<svg
												class="mr-3 h-4 w-4 shrink-0 text-zinc-500 dark:text-zinc-400"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
												/>
											</svg>
											{formatDate(event.date)} • {formatTime(event.start_time)} - {formatTime(
												event.end_time
											)}
										</div>
										<div class="flex items-start">
											<svg
												class="mt-0.5 mr-3 h-4 w-4 shrink-0 text-zinc-500 dark:text-zinc-400"
												fill="none"
												viewBox="0 0 24 24"
												stroke="currentColor"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
												/>
											</svg>
											<span>{event.venue}</span>
										</div>
									</div>
									<p class="mt-4 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">
										{event.details}
									</p>
								</div>
							</div>
						</div>
					</article>
				{/each}
			</div>
		</div>
	</main>
</div>
