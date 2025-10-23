import json
import ollama
import subprocess

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
You are an expert SQL query generator.
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

# --- Step 5: Run main ---
if __name__ == "__main__":
    start_chat()