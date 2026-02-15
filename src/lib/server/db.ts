import { MongoClient } from 'mongodb';
import { env } from '$env/dynamic/private';

const MONGODB_URI = env.MONGODB_URI || 'mongodb://localhost:27017';
const DB_NAME = env.MONGODB_DB_NAME || 'hackgenix';

const client = new MongoClient(MONGODB_URI);
const db = client.db(DB_NAME);

export { client, db };
