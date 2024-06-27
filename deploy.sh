rsync -rv . --exclude ".git" --exclude ".idea" --exclude "mongo.json" --exclude "__pycache__" --exclude ".python_version" rpi5dl:~/gamebot/

#ssh rpi5dl "cd gamebot/ ; ./restart.sh"