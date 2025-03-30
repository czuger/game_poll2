cat << 'EOF' | ssh pw
cd python/game_bot2_prod
git pull
pip install --upgrade pip
pip install .
supervisorctl restart game_bot2_prod
pyenv version
EOF
