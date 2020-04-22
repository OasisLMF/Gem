#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
file_docker='docker/Dockerfile'
file_versions='data_version.json'
cd $SCRIPT_DIR


# Fetch & extract model data
    make -C model_data/GMO/


# Set Oasis versions 
    env_vars=('OASIS_API_VER' 'OASIS_UI_VER' 'MODEL_VER' 'MODEL_DATA_VER' 'KEYS_DATA_VER')
    for var_name in "${env_vars[@]}"; do
            var_value=$(cat $file_versions | grep $var_name | awk -F'"' '{ print $4 }')
        export $var_name=$var_value
    done


# Run API, UI & Worker
    docker-compose -f docker-compose.yml --project-directory $SCRIPT_DIR up -d --build
