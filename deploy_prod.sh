rsync -rv . --exclude ".git" --exclude ".idea" --exclude "config.json" --exclude "__pycache__" --exclude ".python_version" --exclude "docker-compose.yml" pw:~/python/gamebot/

ssh pw "supervisorctl restart gamebot2"