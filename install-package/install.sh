#install dependencies
echo installing dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip dos2unix

#prepare files
echo preparing src files
cd ./src
dos2unix main.py
dos2unix terminalmon.py
dos2unix utils.py
chmod +x main.py
cd ..

#ensure json is empty
echo cleaning json folder
cd ./json
rm -r *
cd ..

#tmon handling
echo setting up tmon daemon
chmod +x tmon
dos2unix tmon
mkdir -p ~/bin
mv tmon ~/bin/
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

#add xp traching to bashrc
echo adding xp tracking to bashrc
bash -c '
BASHRC="$HOME/.bashrc"
MARKER="# TerminalMon XP Hook"
if ! grep -q "$MARKER" "$BASHRC"; then
  cat <<EOF >> "$BASHRC"

$MARKER
function terminalmon_xp_tracker() {
    local last_command=\$(HISTTIMEFORMAT= history 1 | sed "s/^ *[0-9]* *//")

    if [[ "\$last_command" == tmon* ]]; then
        return
    fi

    local cmd_length=\${#last_command}
    if [[ \$cmd_length -gt 0 ]]; then
        tmon xp "\$cmd_length" > /dev/null 2>&1
    fi
}

if [[ \$- == *i* ]]; then
    PROMPT_COMMAND="terminalmon_xp_tracker; \$PROMPT_COMMAND"
fi
EOF
  echo "✅ TerminalMon XP tracker added to ~/.bashrc"
else
  echo "⚠️ TerminalMon XP tracker already exists in ~/.bashrc"
fi
'
source ~/.bashrc

#run app on startup
echo running app and daemon..... please wait
cd ./src
./main.py 
python3 daemon.py &