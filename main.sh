#!/bin/bash
######################################
#
# Template shell pour porvoir coder avec plusieurs fichiers dépendants facilement
# L'arborescence cible est dans l'état :
# ./[le point d'entrée]
# ./lib/[les dépendances]
#
######################################

######################################
# Imports
######################################
BASEDIR=$(dirname "$0")
# Déclaration des noms de fichiers dans le répertoire des dépendances 
IMPORTS=(
    $(ls ./lib)
) # l'ordre d'import n'importe pas, une fois les fichiers sourcés chacunes des fonctions appelées depuis $0 peut utiliser chacune des dépendances, 
# attention à la surcharge de noms de variables !

# Import des fonctions et variables de ces fichiers avec arrêt du script en cas d'erreur
for dependancy in ${IMPORTS[@]}; do
    echo -n "Importing ${BASEDIR}/lib/${dependancy}"
    source ${BASEDIR}/lib/${dependancy}
    status="$?"
    if [ $status -ne "0" ]; then
        echo -e "\e[91m ${BASEDIR}/lib/${dependancy} could not be sourced !
        Stopping $0. \e[0m"
        exit 1
    fi
    echo "... Status : [${status}]"
done

# Pour vérifier quelles fonctions sont accessibles : 
print_avalaible_functions() {
    print_title "Fonctions disponibles"
    VAR=()
    VAR+=$(declare -F)
    print "${VAR//'declare -f'/}"
    print_separator
}

script_title

while :; do
    1_choose_a_use_case_name
    2_ask_for_characteristic_informations
    3_ask_for_main_success_scenario
    4_ask_for_extensions
    5_ask_for_sub_variation
    convert_a_specification ${use_case_outputfilename}
done
exit_ok
