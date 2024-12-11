# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples
export PATH=$PATH:/home/c181dsx0939/seiscomp/bin
export SEISCOMP_ROOT="/home/c181dsx0939/seiscomp"
export PATH="/home/c181dsx0939/seiscomp/bin:$PATH"
export LD_LIBRARY_PATH="/home/c181dsx0939/seiscomp/lib:/usr/local/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="/home/c181dsx0939/seiscomp/lib/python:$PYTHONPATH"
export MANPATH="/home/c181dsx0939/seiscomp/share/man:$MANPATH"
source "/home/c181dsx0939/seiscomp/share/shell-completion/seiscomp.bash"

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
#alias ll='ls -l'
#alias la='ls -A'
#alias l='ls -CF'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
