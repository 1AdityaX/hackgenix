<script lang="ts">
	import timetable from '$lib/course/timetable.json';
	import studentCourse from '$lib/course/studentCourse.json';

	type TimetableEntry = {
		time: string;
		subject: string;
		teacher: string | null;
		room: string;
	};

	const batch = 'Batch C';
	const daysOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

	let activeTab: 'all' | 'mine' = 'all';

	const allTimetable: Record<string, TimetableEntry[]> = (timetable as any)[batch] ?? {};
	const myCourses = studentCourse.student.courses as Array<{
		id: number;
		subject: string;
		teacher: string;
		schedule: Array<{ day: string; time: string; room: string }>;
	}>;

	function parseTimeToMinutesDaytime(time: string): number {
		// Supports formats like "1:00", "13:00", "1:00 PM", "1 PM"
		const m = time.trim().match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?$/i);
		if (!m) return Number.MAX_SAFE_INTEGER;
		let hour = parseInt(m[1] || '0', 10);
		const minute = parseInt(m[2] || '0', 10);
		const meridiem = (m[3] || '').toUpperCase();

		if (meridiem === 'AM') {
			if (hour === 12) hour = 0; // 12 AM -> 0
		} else if (meridiem === 'PM') {
			if (hour !== 12) hour += 12; // add 12 except for 12 PM
		} else {
			// No meridiem provided: assume day-time policy
			// Treat 1..7 as PM (13..19). Others remain as-is.
			if (hour >= 1 && hour <= 7) hour += 12;
		}
		return hour * 60 + minute;
	}

	function formatDisplayTimeDaytime(time: string): string {
		const m = time.trim().match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?$/i);
		if (!m) return time;
		let hour = parseInt(m[1] || '0', 10);
		const minute = parseInt(m[2] || '0', 10);
		let meridiem = (m[3] || '').toUpperCase();

		if (!meridiem) {
			// Infer meridiem for display: 1–7 and 12 as PM, 8–11 as AM
			if (hour === 12 || (hour >= 1 && hour <= 7)) meridiem = 'PM';
			else meridiem = 'AM';
		}

		// Normalize to h:mm AM/PM format
		let h12 = hour;
		if (meridiem === 'AM') {
			if (hour === 0 || hour === 12) h12 = 12;
		} else if (meridiem === 'PM') {
			if (hour > 12) h12 = hour - 12;
			if (hour === 12) h12 = 12;
		}
		const mm = minute.toString().padStart(2, '0');
		return `${h12}:${mm} ${meridiem}`;
	}

	function extractTimeRange(raw: string): { start?: string; end?: string } {
		// Handles variants like "02:00  -  03:25" or "02:00 - 03:25"
		const match = raw.match(/(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})/);
		if (match) {
			return { start: match[1], end: match[2] };
		}
		return { start: raw.trim() };
	}

	function formatRangeDisplay(raw: string): string {
		const { start, end } = extractTimeRange(raw);
		if (start && end)
			return `${formatDisplayTimeDaytime(start)} - ${formatDisplayTimeDaytime(end)}`;
		if (start) return formatDisplayTimeDaytime(start);
		return raw;
	}

	function getMyByDay(day: string) {
		const items: Array<{ subject: string; teacher: string; time: string; room: string }> = [];
		for (const course of myCourses) {
			for (const slot of course.schedule) {
				if (slot.day.toLowerCase() === day.toLowerCase()) {
					items.push({
						subject: course.subject,
						teacher: course.teacher,
						time: slot.time,
						room: slot.room
					});
				}
			}
		}
		// Sort using normalized daytime minutes of range start
		items.sort((a, b) => {
			const sa = extractTimeRange(a.time).start ?? a.time;
			const sb = extractTimeRange(b.time).start ?? b.time;
			return parseTimeToMinutesDaytime(sa) - parseTimeToMinutesDaytime(sb);
		});
		return items;
	}

	function getAllByDay(day: string): TimetableEntry[] {
		const entries = (allTimetable[day] || []).slice();
		entries.sort((a, b) => {
			const sa = extractTimeRange(a.time).start ?? a.time;
			const sb = extractTimeRange(b.time).start ?? b.time;
			return parseTimeToMinutesDaytime(sa) - parseTimeToMinutesDaytime(sb);
		});
		return entries;
	}

	function tabButtonClass(isActive: boolean): string {
		const base = 'px-3 py-2 rounded-t-lg border text-sm font-medium transition-colors';
		const inactive =
			'border-transparent text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800';
		const active =
			'bg-zinc-900 text-white border-zinc-900 dark:bg-zinc-100 dark:text-zinc-900 dark:border-zinc-100';
		return `${base} ${isActive ? active : inactive}`;
	}
</script>

<section class="mx-auto h-screen max-w-5xl overflow-auto p-4">
	<header class="mb-4 flex gap-2 border-b border-zinc-200 dark:border-zinc-800">
		<button class={tabButtonClass(activeTab === 'all')} on:click={() => (activeTab = 'all')}
			>All Timetable</button
		>
		<button class={tabButtonClass(activeTab === 'mine')} on:click={() => (activeTab = 'mine')}
			>My Timetable</button
		>
	</header>

	{#if activeTab === 'all'}
		<div>
			<h2 class="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
				All Timetable — {batch}
			</h2>
			<div
				class="overflow-auto rounded-lg border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900"
			>
				<table class="w-full text-sm">
					<thead class="bg-zinc-50 dark:bg-zinc-950">
						<tr>
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
								>Day</th
							>
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
								>Time</th
							>
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
								>Subject</th
							>
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
								>Professor</th
							>
							<th
								class="border-b border-zinc-200 px-3 py-2 text-left font-semibold text-zinc-600 dark:border-zinc-800 dark:text-zinc-300"
								>Room</th
							>
						</tr>
					</thead>
					<tbody>
						{#each daysOrder as day}
							{#each getAllByDay(day) as entry}
								<tr class="hover:bg-zinc-50 dark:hover:bg-zinc-800">
									<td
										class="border-b border-zinc-100 px-3 py-2 font-semibold whitespace-nowrap text-zinc-700 dark:border-zinc-800 dark:text-zinc-300"
										>{day}</td
									>
									<td
										class="border-b border-zinc-100 px-3 py-2 text-zinc-900 dark:border-zinc-800 dark:text-zinc-100"
										>{formatRangeDisplay(entry.time)}</td
									>
									<td
										class="border-b border-zinc-100 px-3 py-2 text-zinc-900 dark:border-zinc-800 dark:text-zinc-100"
										>{entry.subject}</td
									>
									<td
										class="border-b border-zinc-100 px-3 py-2 text-zinc-900 dark:border-zinc-800 dark:text-zinc-100"
										>{entry.teacher ?? '-'}</td
									>
									<td
										class="border-b border-zinc-100 px-3 py-2 text-zinc-900 dark:border-zinc-800 dark:text-zinc-100"
										>{entry.room}</td
									>
								</tr>
							{/each}
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		<div>
			<h2 class="mb-3 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
				My Timetable — {studentCourse.student.name}
			</h2>
			<div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
				{#each daysOrder as day}
					<div
						class="rounded-lg border border-zinc-200 bg-white p-3 dark:border-zinc-800 dark:bg-zinc-900"
					>
						<h3 class="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-100">{day}</h3>
						<ul class="space-y-2">
							{#each getMyByDay(day) as item}
								<li
									class="rounded-lg border border-zinc-100 bg-zinc-50 p-2 dark:border-zinc-800 dark:bg-zinc-950"
								>
									<div class="mb-1 font-semibold text-zinc-900 dark:text-zinc-100">
										{item.subject}
									</div>
									<div
										class="flex flex-wrap items-center gap-1.5 text-xs text-zinc-700 dark:text-zinc-300"
									>
										<span>{formatRangeDisplay(item.time)}</span>
										<span class="text-zinc-400 dark:text-zinc-500">•</span>
										<span>{item.teacher}</span>
										<span class="text-zinc-400 dark:text-zinc-500">•</span>
										<span>{item.room}</span>
									</div>
								</li>
							{:else}
								<li
									class="border border-zinc-200 dark:border-zinc-800 rounded-lg p-2 border-dashed text-center text-zinc-500 dark:text-zinc-400"
								>
									No classes
								</li>
							{/each}
						</ul>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</section>
