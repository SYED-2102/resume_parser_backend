import os
from dotenv import load_dotenv

print("--- SYSTEM DIAGNOSTIC ---")
# 1. Where is Python actually running?
current_dir = os.getcwd()
print(f"1. Current Working Directory: {current_dir}")

# 2. What files does Python actually see?
files_in_dir = os.listdir(current_dir)
print(f"2. Files visible in this directory: {files_in_dir}")

# 3. Does it see the .env file specifically?
if ".env" in files_in_dir:
    print("3. File check: .env EXISTS in the correct format.")
elif ".env.txt" in files_in_dir:
    print("3. File check: FAILED. You named it .env.txt because Windows hid the extension.")
else:
    print("3. File check: FAILED. The .env file is completely missing from this folder.")

# 4. Attempt the load
loaded = load_dotenv()
print(f"4. Did dotenv successfully load a file? {loaded}")

# 5. Check the variable
key = os.environ.get("GROQ_API_KEY")
print(f"5. GROQ_API_KEY value: {key}")
print("-------------------------")