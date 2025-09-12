<script>
	// Svelte 5 props API
	let {
		placeholder = 'Ask anything',
		disabled = false,
		loading = false,
		value = '',
		maxRows = 8
	} = $props();

	let text = $state(value);
	/** @type {HTMLTextAreaElement | null} */
	let textareaEl = null;

	function autoResize() {
		if (!textareaEl) return;
		textareaEl.style.height = 'auto';
		const line = parseFloat(getComputedStyle(textareaEl).lineHeight || '20');
		const maxH = line * maxRows;
		textareaEl.style.height = Math.min(textareaEl.scrollHeight, maxH) + 'px';
	}
	/** @param {KeyboardEvent} e */
	function handleKeyDown(e) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			send();
		}
	}

	function send() {
		if (disabled || loading) return;
		const msg = (text || '').trim();
		if (!msg) return;
		// Emit a 'send' event with the message text
		dispatchEvent(new CustomEvent('send', { detail: { text: msg }, bubbles: true }));
		text = '';
		queueMicrotask(autoResize);
	}

	$effect(() => {
		text = value ?? text;
	});
	$effect(() => {
		// Depend on text so this runs when the input changes
		text;
		autoResize();
	});
</script>

<div class="w-full">
	<div
		class="flex items-end gap-2 rounded-xl border border-zinc-300 bg-white p-2 shadow-sm dark:border-zinc-700 dark:bg-zinc-800"
	>
		<textarea
			bind:this={textareaEl}
			class="min-h-[2.5rem] w-full resize-none bg-transparent px-3 py-2 text-base text-zinc-900 placeholder-zinc-400 outline-none focus:ring-0 disabled:opacity-60 dark:text-zinc-100 dark:placeholder-zinc-500"
			{placeholder}
			bind:value={text}
			rows={1}
			oninput={autoResize}
			onkeydown={handleKeyDown}
			disabled={disabled || loading}
			aria-label="Chat message input"
		></textarea>
		<button
			type="button"
			onclick={send}
			disabled={disabled || loading || !(text && text.trim())}
			class="inline-flex h-10 shrink-0 items-center justify-center rounded-lg bg-zinc-900 px-3 text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
			aria-label="Send message"
		>
			{#if loading}
				<svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
					<circle
						class="opacity-25"
						cx="12"
						cy="12"
						r="10"
						stroke="currentColor"
						stroke-width="4"
						fill="none"
					/>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
				</svg>
			{:else}
				<svg
					class="h-5 w-5"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					aria-hidden="true"
				>
					<path d="M22 2L11 13" />
					<path d="M22 2l-7 20-4-9-9-4 20-7z" />
				</svg>
			{/if}
		</button>
	</div>
	<p class="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
		Enter to send · Shift+Enter for newline
	</p>
</div>

<style>
	textarea {
		overflow: hidden;
	}
</style>