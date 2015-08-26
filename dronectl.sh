#!/bin/sh

DRONE_IMAGE="hivemined/drone"

#continer name prefixes for easy discovery
RUNTIME="hivemined-run"
VOLUMES="hivemined-dat"
JARPACK="hivemined-jar"

#check for existence of specified drone
__drone_exists () {
    local name="${VOLUMES}-$1"
    return $(docker ps -a | grep -q "$name")
}

#check if specified drone is running
__drone_running () {
    local name="${VOLUMES}-$1"
    return $(docker ps | grep -q "$name")
}

#check for existence of specified jarpack instance
__jarpack_exists () {
    local name="${JARPACK}-$1"
    return $(docker ps -a | grep -q "$name")
}

#check for the existence of a specified image
__image_exists () {
    return $(docker images | grep -q "$1")
}

#initialize jarpack container from given image
__jarpack_init () {
    __jarpack_exists "$1" && return 0

    if ( ! __image_exists "$2" ) && ( ! __jarpack_pull "$2" ); then
            echo "Error: specified image cannot be found!"
            return 1
        fi
    fi

    docker create --name "${JARPACK}-$1" "$2" true
    return $?
}

#remove specified jarpack container
__jarpack_clean () {
    __jarpack_exists && docker rm -f "${JARPACK}-$1" || return 1
    return 0
}

#build new jarpack image from a given context
__jarpack_build () {
    if __image_exists "$1"; then
        if [ "$3" = --force ]; then
            docker rmi "$1"
        else
            echo "Error: specified jarpack image already exists!"
            return 1
        fi
    fi
    docker build -t "$1" "$2"
    return $?
}

#pull down a jarpack image from the registry
__jarpack_pull () {
    if __image_exists "$1"; then
        if [ "$2" = --force ]; then
            docker rmi "$1"
        else
            echo "Error: specified jarpack image already exists!"
            return 1
        fi
    fi
    docker pull "$1"
    return $?
}

#send command to the specified drone
__drone_cmd () {
    local name="${RUNTIME}-$1"
    if ! __drone_exists "$1"; then
        echo "Error: specified drone instance does not exist!"
        return 1
    fi

    shift
    docker exec "$name" /cmd "$*"
    return $?
}

#create a new drone instance
__drone_create () {
    local name="$1"
    local jarpack="$2"
    strip 2

    __jarpack_exists "$jarpack" || return 1

    while __drone_exists "$name"; do
        if $(echo "$name" | grep -qE -[0-9]+$); then
            base=$(echo "$name" | sed "s/\(.*-\)\([0-9]\+$\)/\1/")
            num=$(echo "$name" | sed "s/\(.*-\)\([0-9]\+$\)/\2/")
            name="${base}$(($num + 1))"
        else
            name="${name}-1"
        fi
    done

    docker create --name "${VOLUMES}-$name" \
        --entrypoint true "$DRONE_IMAGE"

    docker run --name "${RUNTIME}-$name" \
        --volumes-from "${VOLUMES}-$name" \
        --volumes-from "${JARPACK}-$jarpack" "$DRONE_IMAGE" "$*"

    echo "Created drone instance \'$name\' using jarpack \'$jarpack\'"

    return __drone_exists "$name"
}

#delete the specified drone instance
__drone_delete () {
    local name-run="${RUNTIME}-$1"
    local name-dat="${VOLUMES}-$1"
    if ! __drone_exists "$1"; then
        echo "Error: specified drone instance does not exist!"
        return 1
    fi

    __drone_running "$1" && __drone_stop "$1" || return 1
    docker rm -f "$name-run" "$name-dat"
    return $?
}

#rename the specified drone instance
__drone_rename () {
    echo "TODO: implement rename function"
    return 0
}

#start the specified drone instance
__drone_start () {
    local name="${RUNTIME}-$1"
    if ! __drone_exists "$1"; then
        echo "Error: specified drone instance does not exist!"
        return 1
    elif __drone_running "$1"; then
        echo "Error: specified drone is already running!"
        return 1
    fi

    docker start "$name"
    return $?
}

#stop the specified drone instance
__drone_stop () {
    local name="${RUNTIME}-$1"
    if ! __drone_exists "$1"; then
        echo "Error: specified drone instance does not exist!"
        return 1
    elif ! __drone_running "$1"; then
        echo "Error: specified drone is not running!"
        return 1
    fi

    __drone_cmd "$name" "save-world"
    __drone_cmd "$name" "stop"

    while __drone_running "$1"; do
        sleep 1
    done
    return $?
}

#restart the specified drone instance
__drone_restart () {
    __drone_running "$1" && __drone_stop "$1" || return 1
    __drone_start "$1"
    return $?
}

#update the specified drone instance
__drone_update () {
    echo "TODO: implement update function"
    return 0
}

#backup drone instance to host disk
__drone_backup () {
    echo "TODO: implement backup function"
    return 0
}

#restore drone instance from backup
__drone_restore () {
    echo "TODO: implement restore function"
    return 0
}

__drone_main__ () {
    local command="$1"
    local name="$2"
    strip 2

    if   [ "$command" = create  ]; then
        __drone_create "$name" $@

    elif [ "$command" = delete  ]; then
        __drone_delete "$name"

    elif [ "$command" = rename  ]; then
        __drone_rename "$name" "$1"

    elif [ "$command" = start   ]; then
        __drone_start "$name"

    elif [ "$command" = stop    ]; then
        __drone_stop "$name"

    elif [ "$command" = restart ]; then
        __drone_restart "$name"

    elif [ "$command" = update  ]; then
        __drone_update "$name"

    elif [ "$command" = backup  ]; then
        __drone_backup "$name"

    elif [ "$command" = restore ]; then
        __drone_restore "$name" "$1"

    fi
}

__jarpack_main__ () {
    local command="$1"
    local name="$2"
    strip 2

    if   [ "$command" = init ]; then
        __jarpack_init "$name" "$1"

    elif [ "$command" = clean ]; then
        __jarpack_clean "$name"

    elif [ "$command" = build ]; then
        __jarpack_build "$name" "$2" "$3"

    elif [ "$command" = pull ]; then
        __jarpack_pull "$name"

    fi
}

__backup_main__ () {
    #list
    #delete <backup_name>
    #export <backup_name> <destination>
}

__main__ () {
    class="$1"
    strip

    if [ "$class" = drone ]; then
        __drone_main__ $@
    elif [ "$class" = jarpack ]; then
        __jarpack_main__ $@
    elif [ "$class" = backup ]; then
        __backup_main__ $@
    fi
}
