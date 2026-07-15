# TerminalMon XP Hook
function terminalmon_xp_tracker() {
    local last_command=${history[$HISTCMD]}

    if [[ "$last_command" == tmon* ]]; then
        return
    fi

    local cmd_length=${#last_command}
    if [[ $cmd_length -gt 0 ]]; then
        tmon xp "$cmd_length" > /dev/null 2>&1
    fi
}

autoload -Uz add-zsh-hook
add-zsh-hook precmd terminalmon_xp_tracker
