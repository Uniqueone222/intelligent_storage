# Schema Generation Examples

This document shows examples of how the system generates schemas for different types of JSON data.

## Example 1: Simple Flat Structure (SQL)

### Input JSON:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "is_active": true
}
```

### AI Decision: **SQL** (Confidence: 95%)

**Reasoning:** "Flat, consistent structure suitable for relational database"

### Generated SQL Schema:
```sql
CREATE TABLE IF NOT EXISTS user_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    age INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Column Details:
- `id`: SERIAL PRIMARY KEY (auto-increment)
- `name`: VARCHAR(255)
- `email`: VARCHAR(255)
- `age`: INTEGER
- `is_active`: BOOLEAN
- `created_at`: TIMESTAMP

---

## Example 2: Nested Structure (NoSQL)

### Input JSON:
```json
{
  "user": {
    "name": "John Doe",
    "contact": {
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  },
  "orders": [
    {
      "id": 1,
      "items": ["item1", "item2"],
      "total": 99.99
    }
  ],
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

### AI Decision: **NoSQL** (Confidence: 92%)

**Reasoning:** "Deep nesting and complex array structures detected - better suited for document database"

### Generated MongoDB Schema:
```javascript
{
    user: Object,
    orders: Array<Object>,
    preferences: Object,
}
```

### Document Structure:
```
Collection: user_orders
- user: Object (nested)
  - name: String
  - contact: Object
    - email: String
    - phone: String
- orders: Array of Objects
  - id: Number (Int)
  - items: Array of Strings
  - total: Number (Float)
- preferences: Object
  - theme: String
  - notifications: Boolean
```

---

## Example 3: Array of Objects (SQL)

### Input JSON:
```json
[
  {
    "product_id": 1,
    "name": "Widget A",
    "price": 19.99,
    "in_stock": true
  },
  {
    "product_id": 2,
    "name": "Widget B",
    "price": 29.99,
    "in_stock": false
  }
]
```

### AI Decision: **SQL** (Confidence: 98%)

**Reasoning:** "Consistent structure across array items - ideal for relational table"

### Generated SQL Schema:
```sql
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    name VARCHAR(255),
    price REAL,
    in_stock BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Inserted:
- 2 rows inserted into `products` table
- Each array item becomes a table row

---

## Example 4: Mixed Types (NoSQL)

### Input JSON:
```json
{
  "event_name": "User Login",
  "timestamp": "2025-11-15T10:30:00Z",
  "metadata": {
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "custom_data": {
      "session_id": "abc123",
      "referrer": "https://example.com"
    }
  },
  "tags": ["login", "authentication", "success"]
}
```

### AI Decision: **NoSQL** (Confidence: 88%)

**Reasoning:** "Variable structure with deep nesting - NoSQL provides better flexibility"

### Generated MongoDB Schema:
```javascript
{
    event_name: String,
    timestamp: String,
    metadata: Object,
    tags: Array<String>,
}
```

---

## Frontend Display

When you upload JSON data, the frontend displays:

### 🤖 AI Analysis Section:
- **Decision**: SQL or NoSQL badge
- **Confidence**: Percentage score with color coding
- **Reasoning**: AI's explanation for the choice
- **Records Stored**: Count of items inserted

### 📊 Generated Schema Section (SQL):
- **Table Name**: The generated table name
- **CREATE Statement**: Full SQL code with syntax highlighting
- **Columns List**: Each column with its data type

### 📄 Generated Schema Section (NoSQL):
- **Collection Name**: The MongoDB collection name
- **Document Structure**: Field types and nesting

### 📐 Structure Analysis:
- **Nesting Depth**: How many levels deep
- **Nested Objects**: Yes/No
- **Has Arrays**: Yes/No

---

## How It Works

### 1. Structure Analysis
The system analyzes:
- Maximum nesting depth
- Presence of nested objects
- Array fields
- Schema consistency across array items
- Field count and types

### 2. AI Recommendation
Based on analysis:
- **Depth > 3**: Likely NoSQL
- **Has inconsistent structure**: NoSQL
- **Flat and consistent**: SQL
- **Complex nested arrays**: NoSQL
- **Simple arrays of primitives**: SQL

### 3. Schema Generation

**For SQL:**
1. Extract field names and types from sample data
2. Map JSON types to SQL types:
   - string → VARCHAR(255) or TEXT
   - number → INTEGER or REAL
   - boolean → BOOLEAN
   - object/array → JSONB
3. Add id (PRIMARY KEY) and created_at columns
4. Generate CREATE TABLE statement
5. Execute and insert data

**For NoSQL:**
1. Analyze document structure
2. Identify field types
3. Create collection
4. Insert documents as-is
5. Generate schema representation

---

## Try It Yourself!

1. Start the application
2. Go to "Upload JSON Data" tab
3. Paste any JSON (object or array)
4. Click "Upload JSON Data"
5. Watch the AI analyze and generate schema!

### Sample Data to Try:

**Simple (will choose SQL):**
```json
{"id": 1, "name": "Test", "value": 42}
```

**Complex (will choose NoSQL):**
```json
{
  "user": {"profile": {"settings": {"theme": "dark"}}},
  "history": [{"action": "login", "data": {"ip": "1.2.3.4"}}]
}
```

---

## API Response Example

```json
{
  "success": true,
  "storage": {
    "name": "my_dataset",
    "database_type": "SQL",
    "confidence_score": 95,
    "table_name": "my_dataset",
    "record_count": 1
  },
  "ai_analysis": {
    "database_type": "SQL",
    "confidence": 95,
    "reasoning": "Flat, consistent structure suitable for relational DB",
    "suggested_schema": {
      "name": "string",
      "email": "string",
      "age": "integer"
    }
  },
  "generated_schema": {
    "type": "SQL",
    "table_name": "my_dataset",
    "create_statement": "CREATE TABLE IF NOT EXISTS my_dataset (...)",
    "columns": {
      "name": "VARCHAR(255)",
      "email": "VARCHAR(255)",
      "age": "INTEGER"
    }
  },
  "message": "Data stored in SQL database"
}
```

---

## Visual Examples

When viewing in the web interface, schemas are displayed with:

✅ **Syntax Highlighting** - SQL and MongoDB code is color-coded
✅ **Clean Formatting** - Properly indented and readable
✅ **Type Badges** - Clear visual indicators for data types
✅ **Collapsible Sections** - Organize complex information
✅ **Copy-Paste Ready** - Generated SQL can be copied directly

The schema display makes it easy to:
- Understand how your data is stored
- Learn SQL and MongoDB schema patterns
- Debug data structure issues
- Document your database design

---

**Ready to try it?** Start uploading JSON data and watch the intelligent schema generation in action! 🚀
