import { json, type RequestHandler } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const RAG_SERVER_URL = env.PRIVATE_RAG_SERVER_URL || 'http://localhost:8000';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) {
        return json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
        const { query } = await request.json();

        if (!query || typeof query !== 'string') {
            return json({ error: 'Query is required' }, { status: 400 });
        }

        if (query.length > 2000) {
            return json({ error: 'Query too long (max 2000 characters)' }, { status: 400 });
        }

        const url = new URL(RAG_SERVER_URL);
        url.searchParams.set('query', query);
        url.searchParams.set('user_id', locals.user.id);

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('RAG server error:', response.status, errorText);
            return json(
                { error: 'AI service unavailable' },
                { status: 502 }
            );
        }

        const data = await response.json();
        return json(data);
    } catch (error) {
        console.error('Chat proxy error:', error);
        return json(
            { error: 'Failed to process request' },
            { status: 500 }
        );
    }
};
