<script lang="ts">
	import eventsData from '$lib/course/events.json';
	import type { TodoItem, Event } from '$lib/types';
	import { page } from '$app/state';

	let todos = $state<TodoItem[]>([]);
	const events: Event[] = eventsData.events;

	const user = $derived(page.data.user);

	$effect(() => {
		if (!user) return;
		fetch('/api/todos?limit=3')
			.then((r) => r.json())
			.then((data) => {
				todos = data;
			});
	});

	// Get upcoming events (limit to 3)
	const upcomingEvents = events
		.filter((event) => new Date(event.date) >= new Date())
		.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
		.slice(0, 3);

	// Format date for display
	function formatDate(dateString: string): string {
		const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' };
		return new Date(dateString).toLocaleDateString('en-US', options);
	}

	// Format time to 12-hour format
	function formatTime(timeString: string): string {
		const [hours, minutes] = timeString.split(':');
		const hour = parseInt(hours, 10);
		const ampm = hour >= 12 ? 'PM' : 'AM';
		const hour12 = hour % 12 || 12;
		return `${hour12}:${minutes} ${ampm}`;
	}
</script>

<svelte:head>
	<title>HackGenix - Student Life Dashboard</title>
</svelte:head>

<div class="min-h-screen bg-zinc-50 dark:bg-zinc-950">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">Welcome to HackGenix</h1>
			<p class="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
				Your student life dashboard for managing tasks and staying updated with events
			</p>
		</div>

		<!-- Widgets Grid -->
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Todo Widget -->
			<div
				class="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
			>
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Recent Tasks</h2>
					<a
						href="/todo"
						class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
					>
						View all →
					</a>
				</div>

				{#if !user}
					<div class="py-8 text-center">
						<div class="mb-2 text-sm text-zinc-500 dark:text-zinc-400">
							Sign in to view your tasks
						</div>
						<a
							href="/login"
							class="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
						>
							Sign In
						</a>
					</div>
				{:else if todos.length === 0}
					<div class="py-8 text-center">
						<div class="text-sm text-zinc-500 dark:text-zinc-400">No tasks yet</div>
						<a
							href="/todo"
							class="mt-2 inline-flex items-center rounded-md px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-800"
						>
							Add your first task
						</a>
					</div>
				{:else}
					<div class="space-y-3">
						{#each todos as todo}
							<div class="flex items-center space-x-3">
								<div class="flex-shrink-0">
									<div
										class="h-4 w-4 rounded border border-zinc-300 {todo.completed
											? 'border-green-500 bg-green-500'
											: ''} dark:border-zinc-600"
									>
										{#if todo.completed}
											<svg class="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
												<path
													fill-rule="evenodd"
													d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
													clip-rule="evenodd"
												/>
											</svg>
										{/if}
									</div>
								</div>
								<div class="min-w-0 flex-1">
									<p
										class="text-sm {todo.completed
											? 'text-zinc-400 line-through dark:text-zinc-500'
											: 'text-zinc-900 dark:text-zinc-100'} truncate"
									>
										{todo.title}
									</p>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Events Widget -->
			<div
				class="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
			>
				<div class="mb-4 flex items-center justify-between">
					<h2 class="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Upcoming Events</h2>
					<a
						href="/events"
						class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
					>
						View all →
					</a>
				</div>

				{#if upcomingEvents.length === 0}
					<div class="py-8 text-center">
						<div class="text-sm text-zinc-500 dark:text-zinc-400">No upcoming events</div>
					</div>
				{:else}
					<div class="space-y-4">
						{#each upcomingEvents as event}
							<div class="border-l-4 border-blue-500 pl-4">
								<h3 class="truncate text-sm font-medium text-zinc-900 dark:text-zinc-100">
									{event.event_name}
								</h3>
								<div class="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
									{formatDate(event.date)} • {formatTime(event.start_time)}
								</div>
								<div class="mt-1 truncate text-xs text-zinc-500 dark:text-zinc-400">
									{event.venue}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="mt-8">
			<h2 class="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Quick Actions</h2>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<a
					href="/todo"
					class="flex items-center space-x-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
				>
					<div class="flex-shrink-0">
						<svg
							class="h-6 w-6 text-blue-600"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
							/>
						</svg>
					</div>
					<div>
						<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">Manage Tasks</div>
						<div class="text-xs text-zinc-500 dark:text-zinc-400">Create and track your todos</div>
					</div>
				</a>

				<a
					href="/events"
					class="flex items-center space-x-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
				>
					<div class="flex-shrink-0">
						<svg
							class="h-6 w-6 text-green-600"
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
					</div>
					<div>
						<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">View Events</div>
						<div class="text-xs text-zinc-500 dark:text-zinc-400">Check upcoming events</div>
					</div>
				</a>

				<a
					href="/schedule"
					class="flex items-center space-x-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
				>
					<div class="flex-shrink-0">
						<svg
							class="h-6 w-6 text-purple-600"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div>
						<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">Schedule</div>
						<div class="text-xs text-zinc-500 dark:text-zinc-400">View your timetable</div>
					</div>
				</a>

				<a
					href="/chatai"
					class="flex items-center space-x-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
				>
					<div class="flex-shrink-0">
						<svg
							class="h-6 w-6 text-orange-600"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
							/>
						</svg>
					</div>
					<div>
						<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">Chat AI</div>
						<div class="text-xs text-zinc-500 dark:text-zinc-400">Get help with AI assistant</div>
					</div>
				</a>
			</div>
		</div>
	</div>
</div>
