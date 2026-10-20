/** "2025-10-15" -> "Oct 15, 2025" */
export function formatDate(date: string): string {
	return new Date(date).toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

/** "14:30" -> "2:30 PM" */
export function formatTime(time: string): string {
	const [hours, minutes] = time.split(':');
	const hour = Number(hours);
	return `${hour % 12 || 12}:${minutes} ${hour >= 12 ? 'PM' : 'AM'}`;
}
