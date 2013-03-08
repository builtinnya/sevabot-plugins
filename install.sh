#!/usr/bin/env sh
# ======================================================================
# Install Sevabot plugins
# ======================================================================

set -e


# ======================================================================
# Function definitions
# ======================================================================

usage () {
    cat 1>&2 <<EOF
Usage:
    ./install.sh [-h] <SEVABOT-DIRECTORY>

    Options:
        -h    Show help (this text)
EOF
}

test_dir () {
    # Target directory
    local dir
    # Whether show a message
    local quiet

    dir="$1"
    quiet="$2"

    # Does it exist?
    if [ ! -e "$dir" ]
    then
        [ -z "$quiet" ] && echo "\`$dir' does not exist." 1>&2
        return 1
    fi

    # Is it a directory?
    if [ ! -d "$dir" ]
    then
        [ -z "$quiet" ] && echo "\`$dir' is not a directory." 1>&2
        return 1
    fi

    # Can we open it?
    if [ ! -x "$dir" ]
    then
        [ -z "$quiet" ] && echo "\`$dir' cannot be opened." 1>&2
        return 1
    fi
}

install_file () {
    # File to install
    local source
    # Resultant file
    local target

    source="${PWD}/`basename $1`"
    target="$2/`basename $1`"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
        mv "$target" "${target}.bak"
        chmod -x "${target}.bak"
    fi

    ln -sf "$source" "$target"
}

main () {
    # Path to this script
    local self
    # Sevabot custom directory
    local sevabot_custom_dir

    self="$1"
    sevabot_custom_dir="$2"

    [ ! -e "$sevabot_custom_dir" ] && mkdir "$sevabot_custom_dir"

    for f in *
    do
        # Skip this script
        [ "$f" = "$self" ] && continue

        # Install executable or python files
        if [ -x "$f" ] || [ "${f##*.}" = "py" ]
        then
            install_file "$f" "$sevabot_custom_dir"
        fi
    done

    echo "Plugins installed successfully."
    echo "Make sure add \"custom\" to MODULE_PATHS in Sevbot's settings.py \
to enable custom modules."
}


# ======================================================================
# Execution starts here
# ======================================================================

while getopts h opt
do
    case $opt in
        h) usage; exit 0;;
        \?) usage; exit 1;;
    esac
done
shift `expr $OPTIND - 1`

if [ $# -ne 1 ]
then
    usage
    exit 1
fi

self="`basename $0`"

sevabot_dir="$1"
test_dir "$sevabot_dir" || exit 1

sevabot_custom_dir="${sevabot_dir}/custom"
# Make the Sevabot custom directory path absolute
if [ `echo $sevabot_custom_dir | grep -c "^/"` -eq 0 ]
then
    sevabot_custom_dir="$PWD/${sevabot_custom_dir}"
fi

main "$self" "$sevabot_custom_dir"
