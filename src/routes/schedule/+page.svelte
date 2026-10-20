<script lang="ts">
	import studentCourse from '#lib/course/studentCourse.json';
	import timetable from '#lib/course/timetable.json';
	import { formatTime } from '#lib/format.js';

	const { student } = studentCourse;
	const batchTimetable = timetable[student.batch as keyof typeof timetable];
	const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] as const;
	const columns = ['Day', 'Time', 'Subject', 'Professor', 'Room'];
	const tabs = [
		{ id: 'all', label: 'All Timetable' },
		{ id: 'mine', label: 'My Timetable' }
	] as const;

	let activeTab = $state<(typeof tabs)[number]['id']>('all');

	/** Slots are written on a 12-hour clock without AM/PM, e.g. "02:00  -  03:25"; hours 1–7 are afternoon. */
	function to24h(time: string): string {
		const [hours, minutes] = time.trim().split(':').map(Number);
		return `${hours >= 1 && hours <= 7 ? hours + 12 : hours}:${String(minutes).padStart(2, '0')}`;
	}

	function slotStart(slot: string): number {
		const [hours, minutes] = to24h(slot.split('-')[0]).split(':').map(Number);
		return hours * 60 + minutes;
	}

	function formatSlot(slot: string): string {
		return slot
			.split('-')
			.map((t) => formatTime(to24h(t)))
			.join(' - ');
	}

	const bySlot = (a: { time: string }, b: { time: string }) =>
		slotStart(a.time) - slotStart(b.time);

	function allClasses(day: (typeof days)[number]) {
		return batchTimetable[day].toSorted(bySlot);
	}

	function myClasses(day: string) {
		return student.courses
			.flatMap((course) =>
				course.schedule
					.filter((slot) => slot.day === day)
					.map((slot) => ({ ...slot, subject: course.subject, teacher: course.teacher }))
			)
			.sort(bySlot);
	}
</script>

<svelte:head>
	<title>Schedule - HackGenix</title>
</svelte:head>

<section class="mx-auto h-screen w-full max-w-5xl overflow-auto p-4">
	<header class="mb-4 flex gap-2 border-b border-zinc-200 dark:border-zinc-800">
		{#each tabs as tab}
			<button
				class="rounded-t-lg border px-3 py-2 text-sm font-medium transition-colors {activeTab ===
				tab.id
					? 'border-zinc-900 bg-zinc-900 text-white dark:border-zinc-100 dark:bg-zinc-100 dark:text-zinc-900'
					: 'border-transparent text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800'}"
				onclick={() => (activeTab = tab.id)}
			>
				{tab.label}
			</button>
		{/each}
	</header>

	{#if activeTab === 'all'}
		<h2 class="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
			All Timetable — {student.batch}
		</h2>
		<div
			class="overflow-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
		>
			<table class="w-full text-sm">
				<thead class="bg-zinc-50 dark:bg-zinc-950">
					<tr>
						{#each columns as column}
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
							>
								{column}
							</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each days as day}
						{#each allClasses(day) as entry}
							<tr
								class="hover:bg-zinc-50 dark:hover:bg-zinc-800 [&>td]:border-b [&>td]:border-zinc-100 [&>td]:px-3 [&>td]:py-2 [&>td]:text-zinc-900 dark:[&>td]:border-zinc-800 dark:[&>td]:text-zinc-100"
							>
								<td class="font-semibold whitespace-nowrap text-zinc-700 dark:text-zinc-300"
									>{day}</td
								>
								<td>{formatSlot(entry.time)}</td>
								<td>{entry.subject}</td>
								<td>{entry.teacher ?? '-'}</td>
								<td>{entry.room}</td>
							</tr>
						{/each}
					{/each}
				</tbody>
			</table>
		</div>
	{:else}
		<h2 class="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
			My Timetable — {student.name}
		</h2>
		<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
			{#each days as day}
				<div
					class="rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
				>
					<h3 class="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-100">{day}</h3>
					<ul class="space-y-2">
						{#each myClasses(day) as item}
							<li
								class="rounded-lg border border-zinc-100 bg-zinc-50 p-2 dark:border-zinc-800 dark:bg-zinc-950"
							>
								<div class="mb-1 font-semibold text-zinc-900 dark:text-zinc-100">
									{item.subject}
								</div>
								<div
									class="flex flex-wrap items-center gap-1.5 text-xs text-zinc-700 dark:text-zinc-300"
								>
									<span>{formatSlot(item.time)}</span>
									<span class="text-zinc-400 dark:text-zinc-500">•</span>
									<span>{item.teacher}</span>
									<span class="text-zinc-400 dark:text-zinc-500">•</span>
									<span>{item.room}</span>
								</div>
							</li>
						{:else}
							<li
								class="rounded-lg border border-dashed border-zinc-200 p-2 text-center text-zinc-500 dark:border-zinc-800 dark:text-zinc-400"
							>
								No classes
							</li>
						{/each}
					</ul>
				</div>
			{/each}
		</div>
	{/if}
</section>
