<script>
	import ChatInput from '$lib/components/ChatInput.svelte';

	/** @type {Array<{type: 'user' | 'assistant', content: string}>} */
	let messages = $state([]);
	let loading = $state(false);

	/** @param {CustomEvent<{text: string}>} event */
	function handleSend(event) {
		const { text } = event.detail;
		if (!text) return;

		messages = [...messages, { type: 'user', content: text }];
		loading = true;

		setTimeout(() => {
			messages = [
				...messages,
				{
					type: 'assistant',
					content: `I received your message: "${text}". This is a demo response.`
				}
			];
			loading = false;
		}, 1000);
	}
</script>

<svelte:head>
	<title>Chat AI - HackGenix</title>
</svelte:head>

<!-- Chat Area -->
<div class="flex flex-1 flex-col">
	<!-- Header -->
	<header class="border-b border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-900">
		<h1 class="text-xl font-semibold text-zinc-900 dark:text-zinc-100">Chat AI</h1>
	</header>

	<!-- Messages Area -->
	<div class="flex-1 overflow-y-auto p-6">
		<div class="mx-auto max-w-4xl space-y-6">
			{#if messages.length === 0}
				<div class="flex h-full items-center justify-center">
					<div class="text-center">
						<div
							class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100 dark:bg-zinc-800"
						>
							<svg class="h-8 w-8 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
								></path>
							</svg>
						</div>
						<p class="text-lg text-zinc-500 dark:text-zinc-400">Start a conversation</p>
						<p class="mt-1 text-sm text-zinc-400 dark:text-zinc-500">Ask me anything!</p>
					</div>
				</div>
			{:else}
				{#each messages as message}
					<div class="flex {message.type === 'user' ? 'justify-end' : 'justify-start'}">
						<div class="max-w-2xl {message.type === 'user' ? 'ml-12' : 'mr-12'}">
							<div
								class="flex {message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-3"
							>
								<!-- Avatar -->
								<div
									class="h-8 w-8 flex-shrink-0 rounded-full {message.type === 'user'
										? 'bg-zinc-900 dark:bg-zinc-100'
										: 'bg-zinc-200 dark:bg-zinc-700'} flex items-center justify-center"
								>
									{#if message.type === 'user'}
										<svg
											class="h-4 w-4 text-white dark:text-zinc-900"
											fill="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
											/>
										</svg>
									{:else}
										<svg
											class="h-4 w-4 text-zinc-600 dark:text-zinc-300"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
											></path>
										</svg>
									{/if}
								</div>

								<!-- Message Content -->
								<div class="flex-1">
									<div
										class="rounded-2xl border border-zinc-200 bg-white px-4 py-3 shadow-sm dark:border-zinc-700 dark:bg-zinc-800"
									>
										<p class="leading-relaxed text-zinc-900 dark:text-zinc-100">
											{message.content}
										</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Chat Input -->
	<div class="border-t border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
		<div class="mx-auto max-w-4xl">
			<ChatInput placeholder="Type your message..." onsend={handleSend} />
		</div>
	</div>
</div>
