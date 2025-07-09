import os
import subprocess

def process_unity_folders(base_dir):
    """
    Loops through all subdirectories in the Unity folder,
    finds `*_referential_statements.json`, and processes each one.
    """
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)

        if not os.path.isdir(folder_path):
            continue  # Skip if not a directory

        # Look for a file ending with "_referential_statements.json"
        
        
        for file in os.listdir(folder_path):
            """ if folder != "livingroom_3":
                continue """
            if file.endswith("_referential_statements.json"):
                input_file = os.path.join(folder_path, file)
                output_file = os.path.join(folder_path, "new_dataset.csv")

                print(f"Processing: {input_file} -> {output_file}")

                # Run the main script with this input and output path
                subprocess.run(["python3", "create_dataset_new.py", input_file, output_file], check=True)
                break  # Process only one matching file per folder

if __name__ == "__main__":
    unity_folder = "../vla_3d_visualizer/datasets/Unity"
    process_unity_folders(unity_folder)
