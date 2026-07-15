# TerminalMon XP Hook
function terminalmon_xp_tracker() {
    local last_command=$(HISTTIMEFORMAT= history 1 | sed "s/^ *[0-9]* *//")

    if [[ "$last_command" == tmon* ]]; then
        return
    fi

    local cmd_length=${#last_command}
    if [[ $cmd_length -gt 0 ]]; then
        tmon xp "$cmd_length" > /dev/null 2>&1
    fi
}

if [[ $- == *i* ]]; then
    PROMPT_COMMAND="terminalmon_xp_tracker; $PROMPT_COMMAND"
fi
