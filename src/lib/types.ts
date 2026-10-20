export interface TodoItem {
	id: string;
	title: string;
	completed: boolean;
	createdAt: string;
}

export interface CampusEvent {
	event_id: string;
	event_name: string;
	date: string;
	start_time: string;
	end_time: string;
	venue: string;
	details: string;
}
