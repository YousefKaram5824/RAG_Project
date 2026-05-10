from controllers.ProjectController import ProjectController
import os
import re # Regex
import uuid

def generate_random_string():
    return uuid.uuid4().hex[:8]

def generate_unique_filepath(orig_file_name: str, project_id: str):

        random_key = generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_file_name = get_clean_file_name(
            orig_file_name=orig_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

def get_clean_file_name(orig_file_name: str):
    cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())
    cleaned_file_name = cleaned_file_name.replace(" ", "_")
    return cleaned_file_name