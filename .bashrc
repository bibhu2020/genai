# ~/.bashrc: executed by bash(1) for non-login shells.

# --- Interactive shell setup ---
# Don't exit shell on error
case $- in
    *i*) set +e ;;
esac

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return ;;
esac

# --- History settings ---
HISTCONTROL=ignoreboth          # ignore duplicates & lines starting with space
shopt -s histappend             # append, don't overwrite
HISTSIZE=1000
HISTFILESIZE=2000

# Check window size after each command
shopt -s checkwinsize

# Enable recursive globbing if needed
# shopt -s globstar

# Make less more friendly
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh /usr/bin/lesspipe)"

# Set chroot info (for prompt)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# --- Color prompt setup ---
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes ;;
esac

# If terminal supports color
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    else
        color_prompt=
    fi
fi

# Default PS1 (used as fallback)
if [ "$color_prompt" != yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi

# Set xterm title
case "$TERM" in
    xterm*|rxvt*)
        PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
        ;;
esac

# --- Aliases ---
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'


# --- Load custom aliases ---
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# --- Enable programmable completion ---
if ! shopt -oq posix; then
    if [ -f /usr/share/bash-completion/bash_completion ]; then
        . /usr/share/bash-completion/bash_completion
    elif [ -f /etc/bash_completion ]; then
        . /etc/bash_completion
    fi
fi

# --- Starting directory & PATH ---
cd /home/azureuser/ws || true
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# --- Conda initialization ---
__conda_setup="$('/home/azureuser/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
elif [ -f "/home/azureuser/miniconda3/etc/profile.d/conda.sh" ]; then
    . "/home/azureuser/miniconda3/etc/profile.d/conda.sh"
else
    export PATH="/home/azureuser/miniconda3/bin:$PATH"
fi
unset __conda_setup
export CONDA_CHANGEPS1=false  # prevent conda from changing prompt

# --- GitHub Actions runner (GitHub Agent Server)---
if [ -d "$HOME/actions-runner" ]; then
    RUNNER_PROCESS=$(pgrep -fo "$HOME/actions-runner/bin/Runner.Listener run")
    if [ -z "$RUNNER_PROCESS" ]; then
        echo "Starting GitHub Actions runner..."
        cd "$HOME/actions-runner"
        nohup ./run.sh > runner.log 2>&1 &
    else
        echo "GitHub Actions runner already running with PID $RUNNER_PROCESS"
    fi
fi

# --- Auto-start MLOps Docker servers ---
if [ -d "$HOME/ws/genai/mlopsserver" ]; then
    (
        echo "Setup environment variables..."
        . "$HOME/ws/genai/mlopsserver/env.sh"
        echo "Start MLOps servers..."
        . "$HOME/ws/genai/mlopsserver/start.sh"
        echo "Cleanup diskspace..."
        . "$HOME/ws/genai/mlopsserver/cleanup_runner.sh"
    )
    # cd "$HOME/ws/genai/ml/ed_003" || echo "⚠ cd to ws failed"
    # . "$HOME/ws/genai/ml/ed_003/setup.sh"
fi

# --- Fancy colored Bash prompt ---
function parse_git_branch {
    git rev-parse --abbrev-ref HEAD 2>/dev/null | sed 's/.*/ &/'
}

function set_bash_prompt {
    local env=""
    [[ -n "$CONDA_DEFAULT_ENV" ]] && env="(${CONDA_DEFAULT_ENV##*/}) "

    local git_branch="$(parse_git_branch)"

    PS1=""
    PS1+="\[\e[30;48;5;82m\] ${env}\u@\h \[\e[0m\]"
    PS1+="\[\e[30;48;5;33m\] \w \[\e[0m\]"
    [[ -n "$git_branch" ]] && PS1+="\[\e[30;48;5;141m\] ${git_branch} \[\e[0m\]"
    PS1+=" \[\e[1;32m\]❯\[\e[0m\] "
}

PROMPT_COMMAND=set_bash_prompt
