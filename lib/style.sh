#!/bin/bash

export RAZ_STYLE="\e[0m"
export BLUE_STYLE="\e[0;49;96m"
export PURPLE_STYLE="\e[1;40;35m"
export RED_STYLE="\e[91m"
export GREEN_STYLE="\e[38;5;82m"
export UDERLINE_STYLE="\e[4m"
export PROMPT_STYLE="\e[0;49;92m"
export ORANGE_STYLE="\e[0;40;93m"

wait_for_user_confirmation() {
    OK=
    read OK
}
print_separator() {
    ## Affiche un séparateur
    echo -e "  ${UDERLINE_STYLE}                                                ${RAZ_STYLE}"
    echo
}
print_title() {
    ## Affiche un titre, prends le titre en paramètre
    print_separator
    echo -e " ${PROMPT_STYLE}         $1         $RAZ_STYLE "
    print_separator
}
print() {
    echo -e "${PROMPT_STYLE} $1 ${RAZ_STYLE}"
}
# pour normaliser l'affichage menu, prends deux paramètres, le numéro de l'item, et le label
prompt_menu_item() {
    if [[ $2 ]]; then 
        echo -e "${ORANGE_STYLE} $1 \t ${BLUE_STYLE} -->  $2 ${RAZ_STYLE}"
    else 
        echo -e "${ORANGE_STYLE} --> $1 ${RAZ_STYLE}"
    fi
}
exit_ok() {
    print "Bonne journée !"
    exit 0
}


