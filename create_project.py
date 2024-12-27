import os
import argparse
from jinja2 import Environment, FileSystemLoader

def create_project_dir(project_name, git_repo=None):
    """
    Creates a project directory with the given name, 
    generates files using Jinja2 templates, 
    and optionally clones a Git repository.

    Args:
        project_name (str): The name of the project directory.
        git_repo (str, optional): The URL of the Git repository to clone.
    """

    try:
        os.makedirs(project_name)
    except FileExistsError:
        print(f"Directory '{project_name}' already exists.")
        return

    env = Environment(loader=FileSystemLoader('.'))

    # Render templates
    dockerfile_template = env.get_template('Dockerfile.j2')
    dockerfile_content = dockerfile_template.render(project_name=project_name)
    with open(os.path.join(project_name, 'Dockerfile'), 'w') as f:
        f.write(dockerfile_content)

    compose_template = env.get_template('docker-compose.yml.j2')
    compose_content = compose_template.render(project_name=project_name)
    with open(os.path.join(project_name, 'docker-compose.yml'), 'w') as f:
        f.write(compose_content)

    makefile_template = env.get_template('Makefile.j2')
    makefile_content = makefile_template.render(project_name=project_name)
    with open(os.path.join(project_name, 'Makefile'), 'w') as f:
        f.write(makefile_content)

    if git_repo:
        os.makedirs(os.path.join(project_name, 'src'))
        try:
            subprocess.run(['git', 'clone', git_repo, os.path.join(project_name, 'src')], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning Git repository: {e}")

    print(f"Project directory '{project_name}' created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new project directory with Docker Compose support.")
    parser.add_argument("project_name", help="The name of the project directory.")
    parser.add_argument("--git-repo", help="The URL of the Git repository to clone.")
    args = parser.parse_args()

    create_project_dir(args.project_name, args.git_repo)