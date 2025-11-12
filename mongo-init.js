// mongo-init.js (message part)

db = db.getSiblingDB("messagesdb");
db.createCollection("message", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "user_id", "user_name", "timestamp", "message"],
      properties: {
        id:        { bsonType: "string" },
        user_id:   { bsonType: "string" },
        user_name: { bsonType: "string" },
        timestamp: { bsonType: "string" },
        message:   { bsonType: "string" }
      }
    }
  }
});

db.message.createIndex({ id: 1 }, { unique: true });
db.message.createIndex({ user_name: 1 });
db.message.createIndex({ timestamp: -1 });

db = db.getSiblingDB("messagesdb");
db.createCollection("messages_info");
db.messages_info.insertOne({ _id: "global", count: 0 });

