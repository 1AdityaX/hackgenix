/**
 * Shared type definitions used across multiple components.
 */

export interface TodoItem {
    id: string;
    title: string;
    completed: boolean;
    createdAt: string;
}

export interface Event {
    event_id: string;
    event_name: string;
    date: string;
    start_time: string;
    end_time: string;
    venue: string;
    details: string;
}
