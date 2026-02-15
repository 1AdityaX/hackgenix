<script lang="ts">
	import type { TodoItem } from '$lib/types';
	import { page } from '$app/state';
	import { Check } from '@lucide/svelte';

	type Filter = 'all' | 'active' | 'completed';

	let todos = $state<TodoItem[]>([]);
	let filter = $state<Filter>('all');
	let newTitle = $state('');

	const user = $derived(page.data.user);

	$effect(() => {
		if (!user) return;
		fetchTodos();
	});

	async function fetchTodos() {
		const res = await fetch('/api/todos');
		if (res.ok) {
			todos = await res.json();
		}
	}

	async function addTodo() {
		const title = newTitle.trim();
		if (!title || !user) return;
		const res = await fetch('/api/todos', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ title })
		});
		if (res.ok) {
			const created = await res.json();
			todos = [created, ...todos];
		}
		newTitle = '';
	}

	async function toggleTodo(id: string) {
		const current = todos.find((t) => t.id === id);
		if (!current) return;
		await fetch(`/api/todos/${id}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ completed: !current.completed })
		});
		todos = todos.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t));
	}

	async function removeTodo(id: string) {
		await fetch(`/api/todos/${id}`, { method: 'DELETE' });
		todos = todos.filter((t) => t.id !== id);
	}

	async function clearCompleted() {
		const completed = todos.filter((t) => t.completed);
		await Promise.all(completed.map((t) => fetch(`/api/todos/${t.id}`, { method: 'DELETE' })));
		todos = todos.filter((t) => !t.completed);
	}

	function visibleTodos(): TodoItem[] {
		if (filter === 'active') return todos.filter((t) => !t.completed);
		if (filter === 'completed') return todos.filter((t) => t.completed);
		return todos;
	}

	function remainingCount(): number {
		return todos.filter((t) => !t.completed).length;
	}
</script>

<section class="w-full flex-1 bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
	<div class="mx-auto w-full max-w-2xl px-6 py-8">
		<header class="mb-6">
			<h1 class="text-2xl font-semibold tracking-tight">Todo</h1>
			<p class="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
				Minimal tasks to keep you on track.
			</p>
		</header>

		<div
			class="flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
		>
			<input
				class="flex-1 bg-transparent text-sm outline-none placeholder:text-zinc-400"
				placeholder="Add a new task and press Enter"
				bind:value={newTitle}
				onkeydown={(e) => e.key === 'Enter' && addTodo()}
			/>
			<button
				class="rounded-md bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-40 dark:bg-zinc-100 dark:text-zinc-900"
				disabled={!newTitle.trim() || !user}
				onclick={addTodo}
			>
				Add
			</button>
		</div>

		{#if !user}
			<div
				class="mt-8 rounded-lg border border-dashed border-zinc-200 p-8 text-center text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-400"
			>
				Sign in to manage your tasks.
			</div>
		{:else if todos.length === 0}
			<div
				class="mt-8 rounded-lg border border-dashed border-zinc-200 p-8 text-center text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-400"
			>
				No tasks yet. Add your first task above.
			</div>
		{:else}
			<div class="mt-6 flex items-center justify-between">
				<div class="flex items-center gap-1 text-xs text-zinc-500 dark:text-zinc-400">
					<span>{remainingCount()}</span>
					<span>{remainingCount() === 1 ? 'task' : 'tasks'} left</span>
				</div>
				<div
					class="flex items-center gap-1 rounded-md border border-zinc-200 bg-zinc-100 p-1 dark:border-zinc-800 dark:bg-zinc-900"
				>
					<button
						class="rounded px-2 py-1 text-xs [@media(hover:hover)]:hover:bg-white dark:[@media(hover:hover)]:hover:bg-zinc-800 {filter ===
						'all'
							? 'bg-white dark:bg-zinc-800'
							: ''}"
						class:font-medium={filter === 'all'}
						onclick={() => (filter = 'all')}>All</button
					>
					<button
						class="rounded px-2 py-1 text-xs [@media(hover:hover)]:hover:bg-white dark:[@media(hover:hover)]:hover:bg-zinc-800 {filter ===
						'active'
							? 'bg-white dark:bg-zinc-800'
							: ''}"
						class:font-medium={filter === 'active'}
						onclick={() => (filter = 'active')}>Active</button
					>
					<button
						class="rounded px-2 py-1 text-xs [@media(hover:hover)]:hover:bg-white dark:[@media(hover:hover)]:hover:bg-zinc-800 {filter ===
						'completed'
							? 'bg-white dark:bg-zinc-800'
							: ''}"
						class:font-medium={filter === 'completed'}
						onclick={() => (filter = 'completed')}>Completed</button
					>
				</div>
			</div>

			<ul
				class="mt-3 divide-y divide-zinc-200 overflow-hidden rounded-lg border border-zinc-200 bg-white dark:divide-zinc-800 dark:border-zinc-800 dark:bg-zinc-900"
			>
				{#each visibleTodos() as todo (todo.id)}
					<li class="flex items-center gap-3 px-4 py-3">
						<!-- Custom square checkbox with tick -->
						<input
							id={`todo-${todo.id}`}
							type="checkbox"
							class="peer sr-only"
							checked={todo.completed}
							onchange={() => toggleTodo(todo.id)}
						/>
						<label
							for={`todo-${todo.id}`}
							class="grid h-5 w-5 place-items-center rounded border border-zinc-300 transition-colors peer-checked:border-zinc-900 peer-checked:bg-zinc-900 peer-focus-visible:outline peer-focus-visible:outline-offset-2 peer-focus-visible:outline-zinc-400 dark:border-zinc-700 dark:peer-checked:border-zinc-100 dark:peer-checked:bg-zinc-100 dark:peer-focus-visible:outline-zinc-600"
						>
							<Check
								class="h-3.5 w-3.5 text-white opacity-0 transition-opacity duration-150 peer-checked:opacity-100 dark:text-zinc-900"
							/>
						</label>
						<div class="flex-1 text-sm">
							<p
								class="truncate {todo.completed
									? 'text-zinc-400 line-through dark:text-zinc-500'
									: ''}"
							>
								{todo.title}
							</p>
						</div>
						<button
							class="text-xs text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
							aria-label="Delete"
							onclick={() => removeTodo(todo.id)}>Delete</button
						>
					</li>
				{/each}
			</ul>

			<div class="mt-3 flex items-center justify-end">
				<button
					class="text-xs text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
					onclick={clearCompleted}>Clear completed</button
				>
			</div>
		{/if}
	</div>
</section>
