#!/bin/bash

function install {
    install_binary
    install_man_page
}

function install_binary {
    if [ ! -d "$HOME/.local/bin" ]; then
        mkdir -p "$HOME/.local/bin/"
    fi

    ln -s "$(dirname "$(realpath "$0")")"/applier "$HOME/.local/bin/applier"
    local path="$HOME/.local/bin"
    local bin_export_line="export PATH=\"\$PATH:$path\""

    echo "$bin_export_line"

    add_to_bash "$bin_export_line"
}

function install_man_page {
    local man_dir="$HOME/.local/share/man/man7"

    mkdir -p "$man_dir"

    local script_dir
    script_dir=$(dirname "$(realpath "$0")")
    local man_page="$script_dir/applier.7"

    if [ -f "$man_page" ]; then
        cp "$man_page" "$man_dir/"
        echo "Man page installed successfully in $man_dir"
        local manpath_export_line="export MANPATH=\":${man_dir%man7}\""
        add_to_bash "$manpath_export_line"
    else
        echo "Error: Man page '$man_page' not found!" >&2
        return 1
    fi
}

function add_to_bash() {
    if ! grep -Fxq "$1" "$HOME/.bashrc"; then
        echo "$1" >>"$HOME/.bashrc"
        echo "line $1 successfuly added to bashrc"
    else
        echo "line $1 already present in bashrc"
    fi
}

install_binary
# install_man_page

# install
