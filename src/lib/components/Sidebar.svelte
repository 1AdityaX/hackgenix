<script>
	import Buttons from './Buttons.svelte';
	import {
		Bell,
		Bot,
		Calendar,
		House,
		NotepadText,
		PartyPopper,
		Pen,
		Settings
	} from '@lucide/svelte';
</script>

<div class="flex min-h-screen w-60 flex-col gap-2 bg-zinc-200 pt-5 dark:bg-zinc-900">
	<Buttons name="Home" icon={House} href="/" />
	<Buttons name="Notifications" icon={Bell} />
	<Buttons name="Queries AI" icon={Bot} href="/chatai" />
	<Buttons name="Todo" icon={NotepadText} href="/todo" />
	<Buttons name="Schedule" icon={Calendar} href="/schedule" />
	<Buttons name="Events" icon={PartyPopper} href="/events" />
	<Buttons name="Appointment" icon={Pen} />
	<Buttons name="Settings" icon={Settings} />
</div>
