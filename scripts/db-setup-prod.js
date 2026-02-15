/**
 * Production database setup script.
 * Creates collections and indexes only — no mock data.
 *
 * Usage:
 *   mongosh "mongodb+srv://user:pass@cluster.mongodb.net/hackgenix" scripts/db-setup-prod.js
 *
 * Or with a local connection string:
 *   mongosh mongodb://localhost:27017/hackgenix scripts/db-setup-prod.js
 */

const DB_NAME = "hackgenix";
const db = db.getSiblingDB ? db.getSiblingDB(DB_NAME) : db;

print("=== HackGenix Production DB Setup ===");
print(`Database: ${DB_NAME}`);

// ---------------------------------------------------------------------------
// 1. Create collections (idempotent — skips if they already exist)
// ---------------------------------------------------------------------------
const collections = ["user", "session", "account", "verification", "todos"];
const existing = db.getCollectionNames();

collections.forEach((name) => {
  if (!existing.includes(name)) {
    db.createCollection(name);
    print(`Created collection: ${name}`);
  } else {
    print(`Collection already exists: ${name}`);
  }
});

// ---------------------------------------------------------------------------
// 2. Create indexes (idempotent — MongoDB skips if index already exists)
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
// 3. Summary
// ---------------------------------------------------------------------------
print("\n=== Setup Complete ===");
print("Collections: " + db.getCollectionNames().join(", "));
print("\nNo data was inserted. Users will register through the app.");
