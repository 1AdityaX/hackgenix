<script lang="ts">
	import { Plus, Mic, Send } from '@lucide/svelte';

	let { placeholder = 'Ask anything', onsend, disabled = false } = $props();

	let text = $state('');

	function send() {
		const msg = text?.trim();
		if (!msg || disabled) return;
		onsend?.({ detail: { text: msg } });
		text = '';
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !disabled) {
			e.preventDefault();
			send();
		}
	}
</script>

<div class="w-full">
	<div class="flex items-center gap-3 rounded-2xl bg-zinc-800 px-4 py-3 dark:bg-zinc-800">
		<!-- Plus icon -->
		<button
			type="button"
			class="flex h-6 w-6 items-center justify-center text-white"
			aria-label="Add attachment"
		>
			<Plus class="h-4 w-4" />
		</button>

		<!-- Input field -->
		<input
			type="text"
			class="flex-1 bg-transparent text-white placeholder-zinc-400 outline-none disabled:opacity-50"
			{placeholder}
			bind:value={text}
			onkeydown={handleKeyDown}
			{disabled}
		/>
		<!-- Send button -->
		<button
			type="button"
			onclick={send}
			disabled={!text?.trim() || disabled}
			class="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-600 text-white transition-colors hover:bg-zinc-500 disabled:cursor-not-allowed disabled:opacity-50"
			aria-label="Send message"
		>
			<Send class="h-4 w-4" />
		</button>
	</div>
</div>
