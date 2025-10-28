import json
import ollama
import subprocess
import sqlite3

# --- Step 1: Ensure model availability ---
def ensure_model(model_name):
    """Check if the model exists locally, otherwise pull it."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model_name not in result.stdout:
            print(f"Downloading lightweight model '{model_name}' ...")
            subprocess.run(["ollama", "pull", model_name], check=True)
        else:
            print(f"Model '{model_name}' is already available.")
    except Exception as e:
        print(f"Error checking/pulling model: {e}")
        exit(1)

# --- Step 2: Load metadata from JSON ---
def load_schema(metadata_path="db_metadata.json"):
    """Load and format DB schema from JSON metadata."""
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"Metadata file '{metadata_path}' not found.")
        exit(1)
    
    schema_text = ""
    for table in metadata.get("tables", []):
        schema_text += f"\nTable: {table['name']}\nDescription: {table['description']}\nColumns:\n"
        for col in table["columns"]:
            schema_text += f" - {col['name']} ({col['type']}): {col['description']}\n"
    return schema_text.strip()

# --- Step 3: SQL generation using Ollama ---
def generate_sql(question, schema, model_name="llama3.2:1b"):
    """Generate SQL query using Ollama model."""
    prompt = f"""
You are an expert SQL query generator. Using sqlite3 syntax, write a SQL query to answer the following question.
There should not be any syntax errors in the SQL query following the sqlite3 syntax format.
Based only on the provided database schema, write **only the SQL query** (no explanations, no markdown).
Ensure all table and column names strictly match the schema.

Database Schema:
{schema}

User Request:
{question}

Output:
"""
    response = ollama.generate(model=model_name, prompt=prompt)
    return response["response"].strip()


def execute_sql_query(db_path, sql):
    """Execute SQL query and return results."""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)

        # Fetch results if it's a SELECT query
        if sql.strip().lower().startswith("select"):
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            print("\n--- Query Results ---")
            print(" | ".join(col_names))
            print("-" * 40)
            for row in rows:
                print(" | ".join(str(x) for x in row))
        else:
            conn.commit()
            print(f"\nQuery executed successfully. Rows affected: {cur.rowcount}")
    except Exception as e:
        print(f"\n❌ Error executing SQL: {e}")
    finally:
        conn.close()


def validate_sql_syntax(database_path, sql):
    """Check if SQL syntax is valid in SQLite."""
    try:
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        # SQLite’s 'EXPLAIN' helps test syntax without executing the query
        cur.execute("EXPLAIN " + sql)
        conn.close()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)
    
# --- Step 4: Chat mode ---
def start_chat(model_name="llama3.2:1b", metadata_path="sample_metadata.json"):
    """Start interactive SQL chat session."""
    # ensure_model(model_name)
    schema = load_schema(metadata_path)
    
    print("\nSQL Assistant is ready! Type your questions below.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat. Goodbye!")
            break
        if not user_input:
            continue

        print("\nGenerating SQL...\n")
        sql = generate_sql(user_input, schema, model_name)
        print(f"SQL Query:\n{sql}\n")

        # ✅ Validate SQL syntax
        valid, error = validate_sql_syntax("banking_fb.db", sql)
        if not valid:
            print(f"⚠️ SQL syntax error detected:\n{error}\n")
            continue

        confirm = input("⚠️  Do you want to execute this query on the database? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("❌ Query execution skipped.\n")
            continue

        print("✅ Executing query...\n")
        execute_sql_query("banking_fb.db", sql)

# --- Step 5: Run main ---
if __name__ == "__main__":
    start_chat()