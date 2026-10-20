// Creates the indexes the app relies on (collections are created implicitly). Safe to re-run.
//
//   mongosh mongodb://localhost:27017/hackgenix scripts/db-setup.js
//   docker exec -i hackgenix-mongo mongosh hackgenix < scripts/db-setup.js

// better-auth
db.user.createIndex({ email: 1 }, { unique: true });
db.session.createIndex({ token: 1 }, { unique: true });
db.session.createIndex({ userId: 1 });
db.session.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
db.account.createIndex({ userId: 1 });
db.account.createIndex({ providerId: 1, accountId: 1 });
db.verification.createIndex({ identifier: 1 });
db.verification.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });

// app
db.todos.createIndex({ userId: 1, createdAt: -1 });

print('Indexes ready on: ' + db.getCollectionNames().sort().join(', '));
