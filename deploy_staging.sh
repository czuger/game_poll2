cat << 'EOF' | ssh pw
cd python/game_bot2_staging
git pull
pip install --upgrade pip
pip install .
pyenv version
EOF
