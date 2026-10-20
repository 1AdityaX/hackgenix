import { MongoClient } from 'mongodb';
import { MONGODB_URI, MONGODB_DB_NAME } from '$app/env/private';

const client = new MongoClient(MONGODB_URI);
const db = client.db(MONGODB_DB_NAME);

export { client, db };
