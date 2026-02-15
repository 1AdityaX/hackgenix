import { json, type RequestHandler } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { ObjectId } from 'mongodb';

const todos = db.collection('todos');

export const GET: RequestHandler = async ({ locals, url }) => {
	if (!locals.user) return json({ error: 'Unauthorized' }, { status: 401 });

	const limitParam = url.searchParams.get('limit');
	const limit = limitParam ? parseInt(limitParam, 10) : 0;

	const results = await todos
		.find({ userId: locals.user.id })
		.sort({ createdAt: -1 })
		.limit(limit)
		.toArray();

	const mapped = results.map((doc) => ({
		id: doc._id.toHexString(),
		title: doc.title,
		completed: doc.completed,
		createdAt: doc.createdAt
	}));

	return json(mapped);
};

export const POST: RequestHandler = async ({ request, locals }) => {
	if (!locals.user) return json({ error: 'Unauthorized' }, { status: 401 });

	const { title } = await request.json();
	if (!title || typeof title !== 'string') {
		return json({ error: 'Title is required' }, { status: 400 });
	}

	const doc = {
		_id: new ObjectId(),
		userId: locals.user.id,
		title: title.trim(),
		completed: false,
		createdAt: new Date().toISOString()
	};

	await todos.insertOne(doc);

	return json(
		{
			id: doc._id.toHexString(),
			title: doc.title,
			completed: doc.completed,
			createdAt: doc.createdAt
		},
		{ status: 201 }
	);
};
