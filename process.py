import json
import os
import sys # Import sys to handle potential encoding issues

# --- Configuration ---
INPUT_FOLDER = "unprocessed"
OUTPUT_FOLDER = "processed"
PROMPT_DELIMITER = "---END_PROMPT---" # The string separating prompts in your .txt files

# Default values for the test case structure (can be adjusted)
DEFAULT_TEST_CASE_VALUES = {
    "attack_type": "character_probe",
    "data_type": "text",
    "nist_risk": None,
    "reviewed": False,
    "source": "generated_from_txt",
    "transformations": None
}

# Default values for the test suite structure (can be adjusted)
DEFAULT_TEST_SUITE_VALUES = {
    "behavior": "detection",
    "description": "Generated Test Suite", # You might want to customize this
    "objective": "Test prompts from input file.", # You might want to customize this
}
# --- End Configuration ---

def create_output_folder(folder_path):
    """Creates the output folder if it doesn't exist."""
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Created output folder: {folder_path}")
        except OSError as e:
            print(f"Error creating output folder {folder_path}: {e}")
            sys.exit(1) # Exit if we can't create the output folder

def process_text_file(input_filepath, output_filepath):
    """Reads a .txt file, parses prompts, and writes a .json file."""
    print(f"Processing: {input_filepath}")
    try:
        # Read the entire file content, trying UTF-8 encoding
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # --- DEBUG ---
            print(f"--- Start Raw Content of {os.path.basename(input_filepath)} ---")
            print(repr(content)) # Use repr() to show hidden characters like \n, \r
            print(f"--- End Raw Content ---")
            # --- END DEBUG ---
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filepath}")
        return
    except Exception as e:
        print(f"Error reading file {input_filepath}: {e}")
        return # Skip this file if reading fails

    # Split the content by the delimiter
    raw_prompts = content.split(PROMPT_DELIMITER)
    # --- DEBUG ---
    print(f"--- Result of splitting by '{PROMPT_DELIMITER}' ---")
    print(raw_prompts)
    print(f"--- End Split Result ---")
    # --- END DEBUG ---

    # Prepare the basic JSON structure for this file
    output_json = {
        "test_suite": {
            **DEFAULT_TEST_SUITE_VALUES, # Use default suite values
            "test_cases": []
        }
    }
    # Update description based on filename
    base_filename = os.path.basename(input_filepath)
    output_json["test_suite"]["description"] = f"Generated Test Suite from {base_filename}"


    # Process each extracted prompt
    for raw_prompt in raw_prompts:
        prompt_text = raw_prompt.strip() # Remove leading/trailing whitespace
        if prompt_text: # Only add non-empty prompts
            test_case = {
                **DEFAULT_TEST_CASE_VALUES, # Start with defaults
                "prompt": prompt_text       # Add the actual prompt
            }
            output_json["test_suite"]["test_cases"].append(test_case)

    # Check if any test cases were actually added
    if not output_json["test_suite"]["test_cases"]:
        print(f"Warning: No prompts found or extracted from {input_filepath}. Skipping JSON output.")
        return

    # Write the JSON output file
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4)
        print(f"Successfully created: {output_filepath}")
    except IOError as e:
        print(f"Error writing JSON file {output_filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing {output_filepath}: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the output directory exists
    create_output_folder(OUTPUT_FOLDER)

    # Check if input directory exists
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: Input folder '{INPUT_FOLDER}' not found.")
        print("Please create the folder and place your .txt files inside.")
        sys.exit(1)

    print(f"Looking for .txt files in: {INPUT_FOLDER}")

    processed_count = 0
    # Iterate through all files in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(".txt"):
            input_path = os.path.join(INPUT_FOLDER, filename)
            # Create the output filename by replacing .txt with .json
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            # Process the file
            process_text_file(input_path, output_path)
            processed_count += 1

    if processed_count == 0:
        print("No .txt files found in the input folder.")
    else:
        print(f"\nProcessing complete. Processed {processed_count} file(s).")
    print(f"Output JSON files are located in: {OUTPUT_FOLDER}")
# --- End Main Execution ---