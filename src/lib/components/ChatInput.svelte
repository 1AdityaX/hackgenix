<script>
	let {
		placeholder = 'Ask anything',
		disabled = false,
		loading = false,
		value = '',
		maxRows = 8,
		onsend
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
		const msg = text?.trim();
		if (!msg) return;
		onsend?.({ detail: { text: msg } });
		text = '';
		queueMicrotask(autoResize);
	}

	$effect(() => {
		text = value ?? text;
		autoResize();
	});
</script>

<div class="w-full">
	<div class="relative">
		<div
			class="flex items-end gap-3 rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm focus-within:border-transparent focus-within:ring-2 focus-within:ring-zinc-500 dark:border-zinc-700 dark:bg-zinc-800"
		>
			<textarea
				bind:this={textareaEl}
				class="max-h-32 min-h-[1.5rem] w-full resize-none overflow-hidden bg-transparent px-3 py-2 text-base text-zinc-900 placeholder-zinc-500 outline-none focus:ring-0 disabled:opacity-60 dark:text-zinc-100 dark:placeholder-zinc-400"
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
				class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-white transition-colors hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
				aria-label="Send message"
			>
				{#if loading}
					<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
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
						class="h-4 w-4"
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
	</div>
</div>
