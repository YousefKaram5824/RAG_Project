from controllers import ProjectController
import os
import re # Regex
import uuid

def generate_random_string():
    return uuid.uuid4().hex[:8]

def get_clean_file_name(orig_file_name: str):
    orig_file_name = orig_file_name.strip()
    base, ext = os.path.splitext(orig_file_name)
    base = re.sub(r"[^\w\-]+", "_", base).strip("_")
    ext = re.sub(r"[^\w.]+", "", ext)
    return f"{base}{ext}"

def generate_unique_filepath(orig_file_name: str, project_id: str):

        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = get_clean_file_name(
            orig_file_name=orig_file_name
        )
        random_key = generate_random_string()

        saved_filename = f"{random_key}_{cleaned_file_name}"

        new_file_path = os.path.join(
            project_path,
            saved_filename
        )

        while os.path.exists(new_file_path):
            random_key = generate_random_string()
            saved_filename = f"{random_key}_{cleaned_file_name}"
            new_file_path = os.path.join(
                project_path,
                saved_filename
            )

        return new_file_path, saved_filename

def get_clean_file_name(orig_file_name: str):
    cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
    cleaned_file_name = cleaned_file_name.replace(" ", "_")
    return cleaned_file_name