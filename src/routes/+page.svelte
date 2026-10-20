<script lang="ts">
	import eventsData from '#lib/course/events.json';
	import { formatDate, formatTime } from '#lib/format.js';
	import type { TodoItem, CampusEvent } from '#lib/types.js';
	import { Calendar, Check, ClipboardList, Clock } from '@lucide/svelte';

	let todos = $state<TodoItem[]>([]);

	$effect(() => {
		fetch('/api/todos?limit=3').then(async (res) => {
			if (res.ok) todos = await res.json();
		});
	});

	const upcomingEvents = (eventsData.events as CampusEvent[])
		.filter((event) => new Date(event.date) >= new Date())
		.sort((a, b) => a.date.localeCompare(b.date))
		.slice(0, 3);

	const quickActions = [
		{
			href: '/todo',
			icon: ClipboardList,
			color: 'text-blue-600',
			title: 'Manage Tasks',
			text: 'Create and track your todos'
		},
		{
			href: '/events',
			icon: Calendar,
			color: 'text-green-600',
			title: 'View Events',
			text: 'Check upcoming events'
		},
		{
			href: '/schedule',
			icon: Clock,
			color: 'text-purple-600',
			title: 'Schedule',
			text: 'View your timetable'
		}
	];
</script>

<svelte:head>
	<title>HackGenix - Student Life Dashboard</title>
</svelte:head>

<div class="min-h-screen flex-1 bg-zinc-50 dark:bg-zinc-950">
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<div class="mb-8">
			<h1 class="text-3xl font-bold text-zinc-900 dark:text-zinc-100">Welcome to HackGenix</h1>
			<p class="mt-2 text-lg text-zinc-600 dark:text-zinc-400">
				Your student life dashboard for managing tasks and staying updated with events
			</p>
		</div>

		<div class="grid gap-6 lg:grid-cols-2">
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

				{#if todos.length === 0}
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
						{#each todos as todo (todo.id)}
							<div class="flex items-center space-x-3">
								<div
									class="grid h-4 w-4 shrink-0 place-items-center rounded border {todo.completed
										? 'border-green-500 bg-green-500'
										: 'border-zinc-300 dark:border-zinc-600'}"
								>
									{#if todo.completed}
										<Check class="h-3 w-3 text-white" />
									{/if}
								</div>
								<p
									class="min-w-0 flex-1 truncate text-sm {todo.completed
										? 'text-zinc-400 line-through dark:text-zinc-500'
										: 'text-zinc-900 dark:text-zinc-100'}"
								>
									{todo.title}
								</p>
							</div>
						{/each}
					</div>
				{/if}
			</div>

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
					<div class="py-8 text-center text-sm text-zinc-500 dark:text-zinc-400">
						No upcoming events
					</div>
				{:else}
					<div class="space-y-4">
						{#each upcomingEvents as event (event.event_id)}
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

		<div class="mt-8">
			<h2 class="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-100">Quick Actions</h2>
			<div class="grid gap-4 sm:grid-cols-3">
				{#each quickActions as { href, icon: Icon, color, title, text }}
					<a
						{href}
						class="flex items-center space-x-3 rounded-lg border border-zinc-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
					>
						<Icon class="h-6 w-6 shrink-0 {color}" />
						<div>
							<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">{title}</div>
							<div class="text-xs text-zinc-500 dark:text-zinc-400">{text}</div>
						</div>
					</a>
				{/each}
			</div>
		</div>
	</div>
</div>
