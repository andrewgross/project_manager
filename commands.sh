#!/bin/bash

PROJECT_MANAGER_DIRECTORY=~/Development/project_manager
PROJECTS_DIRECTORY=~/Development

if [ ! -d "$PROJECT_MANAGER_DIRECTORY" ]; then
  echo "Error: project_manager directory not found at $PROJECT_MANAGER_DIRECTORY"
  return 1
fi

create_project() {
  project_name="$1"

  if [ -z "$project_name" ]; then
    echo "Error: Please provide a project name."
    uv run $PROJECT_MANAGER_DIRECTORY/create_project.py --help
    return 1
  fi

  pushd "$PROJECT_MANAGER_DIRECTORY" > /dev/null
    command="uv run create_project.py $@"

    echo $PWD
    echo $command
    $command
  if [ $? -eq 0 ]; then
    popd > /dev/null
    cd "$PROJECTS_DIRECTORY/$project_name"
    echo "Project '$project_name' created successfully and switched directory."
  else
    popd > /dev/null
    echo "Error: Failed to create project '$project_name'."
  fi
}

workon() {
  project_name="$1"

  if [ -z "$project_name" ]; then
    echo "Error: Please provide a project name."
    echo "Usage: workon PROJECT_NAME"
    return 1
  fi

  project_directory="$PROJECTS_DIRECTORY/$project_name"
  if [ ! -d "$project_directory" ]; then
    echo "Error: Project directory '$project_directory' does not exist."
    return 1
  fi

  cd "$project_directory"

  if [ -f Makefile ] && [ -f docker-compose.yml ] && [ -f Dockerfile ]; then
    make up && make shell
  else
    echo "Makefile, docker-compose.yml, and Dockerfile not found in project directory. Skipping make commands."
  fi
}

_workon_autocomplete() {
  local current_word previous_word words_array current_word_index
  COMPREPLY=()
  current_word="${COMP_WORDS[COMP_CWORD]}"
  previous_word="${COMP_WORDS[COMP_CWORD-1]}"
  words_array=("${COMP_WORDS[@]}")
  current_word_index="${COMP_CWORD}"

  if [ "$previous_word" == "workon" ]; then
    COMPREPLY=( $(compgen -d "$PROJECTS_DIRECTORY/$current_word" | sed "s|$PROJECTS_DIRECTORY\/||") )
  fi
}

complete -F _workon_autocomplete workon

export -f create_project workon