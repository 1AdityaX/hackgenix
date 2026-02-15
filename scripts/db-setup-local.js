/**
 * Local development database setup script.
 * Creates collections, indexes, and inserts mock data.
 *
 * Usage:
 *   mongosh mongodb://localhost:27017/hackgenix scripts/db-setup-local.js
 *
 * Or with docker:
 *   docker exec -i hackgenix-mongo mongosh hackgenix < scripts/db-setup-local.js
 */

const DB_NAME = "hackgenix";
const db = db.getSiblingDB ? db.getSiblingDB(DB_NAME) : db;

print("=== HackGenix Local DB Setup ===");
print(`Database: ${DB_NAME}`);

// ---------------------------------------------------------------------------
// 1. Drop existing collections (clean slate for local dev)
// ---------------------------------------------------------------------------
const collections = ["user", "session", "account", "verification", "todos"];
collections.forEach((name) => {
  if (db.getCollectionNames().includes(name)) {
    db[name].drop();
    print(`Dropped collection: ${name}`);
  }
});

// ---------------------------------------------------------------------------
// 2. Create collections
// ---------------------------------------------------------------------------
collections.forEach((name) => {
  db.createCollection(name);
  print(`Created collection: ${name}`);
});

// ---------------------------------------------------------------------------
// 3. Create indexes
// ---------------------------------------------------------------------------

// better-auth: user
db.user.createIndex({ email: 1 }, { unique: true });
print("Index: user.email (unique)");

// better-auth: session
db.session.createIndex({ token: 1 }, { unique: true });
db.session.createIndex({ userId: 1 });
db.session.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
print("Indexes: session.token (unique), session.userId, session.expiresAt (TTL)");

// better-auth: account
db.account.createIndex({ userId: 1 });
db.account.createIndex({ providerId: 1, accountId: 1 });
print("Indexes: account.userId, account.(providerId + accountId)");

// better-auth: verification
db.verification.createIndex({ identifier: 1 });
db.verification.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
print("Indexes: verification.identifier, verification.expiresAt (TTL)");

// todos
db.todos.createIndex({ userId: 1, createdAt: -1 });
print("Index: todos.(userId + createdAt)");

// ---------------------------------------------------------------------------
// 4. Insert mock data
// ---------------------------------------------------------------------------

// Mock user (password hash for "password123" — bcrypt)
const mockUserId = ObjectId().toString();
const now = new Date();

db.user.insertOne({
  _id: mockUserId,
  name: "Test Student",
  email: "student@hackgenix.dev",
  emailVerified: true,
  image: null,
  createdAt: now,
  updatedAt: now,
});
print(`\nMock user created: student@hackgenix.dev`);

// Mock account (email/password credential)
// NOTE: This is a bcrypt hash of "password123" — works with better-auth's default hasher
db.account.insertOne({
  _id: ObjectId().toString(),
  userId: mockUserId,
  accountId: mockUserId,
  providerId: "credential",
  password:
    "$2b$10$K7L1OJ45/4Y2nIvhRVpCe.FSmhDdWoXehVzJptJ/op0lSsvqNChbG",
  accessToken: null,
  refreshToken: null,
  idToken: null,
  accessTokenExpiresAt: null,
  refreshTokenExpiresAt: null,
  scope: null,
  createdAt: now,
  updatedAt: now,
});
print("Mock credential account created (password: password123)");

// Mock todos
const mockTodos = [
  {
    userId: mockUserId,
    title: "Complete Data Structures assignment",
    completed: false,
    createdAt: new Date(now.getTime() - 1000 * 60 * 60).toISOString(),
  },
  {
    userId: mockUserId,
    title: "Review lecture notes for Operating Systems",
    completed: false,
    createdAt: new Date(now.getTime() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    userId: mockUserId,
    title: "Submit math homework",
    completed: true,
    createdAt: new Date(now.getTime() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    userId: mockUserId,
    title: "Prepare for AI/ML quiz",
    completed: false,
    createdAt: new Date(now.getTime() - 1000 * 60 * 60 * 48).toISOString(),
  },
  {
    userId: mockUserId,
    title: "Team meeting for capstone project",
    completed: true,
    createdAt: new Date(now.getTime() - 1000 * 60 * 60 * 72).toISOString(),
  },
];

db.todos.insertMany(mockTodos);
print(`Inserted ${mockTodos.length} mock todos`);

// ---------------------------------------------------------------------------
// 5. Summary
// ---------------------------------------------------------------------------
print("\n=== Setup Complete ===");
print("Collections: " + db.getCollectionNames().join(", "));
print("\nMock credentials:");
print("  Email:    student@hackgenix.dev");
print("  Password: password123");
print("\nYou can now start the app with: npm run dev");
