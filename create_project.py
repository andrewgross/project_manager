# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2",
# ]
# ///
import argparse
import os
import subprocess

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def create_project_dir(project_name, git_repo=None, gpu_count=None, image_name="ubuntu-cuda:v8"):
    """Creates a project directory, renders templates, clones a Git repo, and tags a Docker image."""

    project_path = Path(project_name)
    if not project_path.is_absolute():
        project_path = Path("/home/andrew/Development") / project_name

    project_path.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader('.'))

    # Render templates
    compose_template = env.get_template('docker-compose.yml.j2')
    compose_content = compose_template.render(
        project_name=project_name,
        GPU_COUNT=gpu_count,
        IMAGE_NAME=image_name
    )
    with open(project_path / 'docker-compose.yml', 'w') as f:
        f.write(compose_content)

    makefile_template = env.get_template('Makefile.j2')
    makefile_content = makefile_template.render(project_name=project_name, image_name=image_name)
    with open(project_path / 'Makefile', 'w') as f:
        f.write(makefile_content)

    dockerfile_template = env.get_template('Dockerfile.j2')
    dockerfile_content = dockerfile_template.render(project_name=project_name) # passed the project name to the dockerfile
    with open(project_path / 'Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    src_path = project_path / 'app'
    src_path.mkdir(exist_ok=True)
    if git_repo:
        try:
            subprocess.run(['git', 'clone', git_repo, str(src_path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning Git repository: {e}")

    # Tag the local image with a project-specific name
    try:
        subprocess.run(['docker', 'tag', image_name, f"{project_name}"], check=True)
        print(f"Tagged local image as {project_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error tagging Docker image: {e}. Ensure the image '{image_name}' exists locally.")
        exit(1)

    print(f"Project directory '{project_path}' created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create project with Docker Compose.")
    parser.add_argument("project_name", help="The name of the project.")
    parser.add_argument("--git-repo", help="The URL of the Git repository to clone.")
    parser.add_argument("--gpu-count", type=str, default="-1", help="Number of GPUs or 'all'.")
    parser.add_argument("--image-name", type=str, default="ubuntu-cuda:v8", help="The local Docker image to use") # removed version tag from default image
    args = parser.parse_args()

    # Validate gpu_count
    if args.gpu_count.lower() != "all":
        try:
            gpu_count = int(args.gpu_count)
        except ValueError:
            parser.error("--gpu-count must be an integer or 'all'.")
    else:
        gpu_count = "all"

    create_project_dir(args.project_name, args.git_repo, gpu_count, args.image_name)