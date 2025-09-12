<script>
    import Buttons from "./Buttons.svelte";
     import { Bot, Calendar, House, NotepadText, PartyPopper, Pen, Settings } from '@lucide/svelte';
</script>

<div class="bg-zinc-200 dark:bg-zinc-900 min-h-screen flex flex-col pt-5 w-60 gap-2">
    <Buttons name="Home" icon={House}/>
    <Buttons name="Queries AI" icon={Bot}/>
    <Buttons name="Todo" icon={NotepadText}/>
    <Buttons name="Schedule" icon={Calendar}/>
    <Buttons name="Events" icon={PartyPopper}/>
    <Buttons name="Appointment" icon={Pen}/>
    <Buttons name="Settings" icon={Settings}/>
</div>