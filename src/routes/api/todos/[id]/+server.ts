import { json, type RequestHandler } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { ObjectId } from 'mongodb';

const todos = db.collection('todos');

export const PATCH: RequestHandler = async ({ params, request, locals }) => {
	if (!locals.user) return json({ error: 'Unauthorized' }, { status: 401 });

	const body = await request.json();
	const updates: Record<string, unknown> = {};
	if (typeof body.completed === 'boolean') updates.completed = body.completed;
	if (typeof body.title === 'string') updates.title = body.title;

	if (Object.keys(updates).length === 0) {
		return json({ error: 'No valid fields to update' }, { status: 400 });
	}

	await todos.updateOne(
		{ _id: new ObjectId(params.id), userId: locals.user.id },
		{ $set: updates }
	);

	return json({ ok: true });
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
	if (!locals.user) return json({ error: 'Unauthorized' }, { status: 401 });

	await todos.deleteOne({ _id: new ObjectId(params.id), userId: locals.user.id });

	return json({ ok: true });
};
