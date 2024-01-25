#!/bin/bash

use_case_name=
use_case_number=$(ls ./markdown/ | wc -l)
use_case_outputfilename=
use_case_markdown_folder='markdown'

mkdir markdown
mkdir word

print_to_uc_file() {
    echo "$@" >> ${use_case_outputfilename}
    # le markdown ça aime bien les sauts de lignes
    echo ' ' >> ${use_case_outputfilename}
}
################################################################################
1_choose_a_use_case_name() {
    print "Use case n° ${use_case_number}"
    print "Saisissez le libellé du use case, sans accolades, accents, il sera utilisé pour le nom de fichier : "
    read use_case_name
    use_case_outputfilename='UC'
    use_case_outputfilename="${use_case_markdown_folder}/${use_case_outputfilename}-${use_case_number}_${use_case_name// /_}.md"
    
    print "Le fichier ${use_case_outputfilename} va être créé : laissez vide pour valider, saisissez N pour recommencer :"
    ABORT=
    read ABORT
    if [[ $ABORT ]]; then
        choose_a_use_case_name
    else
        print_to_uc_file "# ${use_case_name}"
        print_to_uc_file "> Date de création : $(date)"
        print_to_uc_file '<hr>'
        
    fi
}

################################################################################
# Je préfère trois tableaux indexés dans le meme ordre qu'autre chose
CHARACTERISTIC_INFORMATION=(
    'Goal in Context:'
    'Scope:'
    'Level:'
    'Preconditions:'
    'Success End Condition:'
    'Failed End Condition:'
    'Primary Actor:'
    'Trigger:'
)
CHARACTERISTIC_INFORMATION_ANSWERS=()
CHARACTERISTIC_INFORMATION_EXPLAINATION=(
    'a longer statement of the goal, if needed'
    'what system is being considered black-box under design'
    'one of: Summary, Primary task, Subfunction'
    'what we expect is already the state of the world'
    'the state of the world upon successful completion'
    'the state of the world if goal abandoned'
    'a role name for the primary actor, or description'
    'the action upon the system that starts the use case, may be time event'
)
2_ask_for_characteristic_informations(){
    for index in ${!CHARACTERISTIC_INFORMATION[@]}; do
        prompt_menu_item "${CHARACTERISTIC_INFORMATION[$index]}" "${CHARACTERISTIC_INFORMATION_EXPLAINATION[$index]}"
        ANSWER=
        read ANSWER
        if [[ -z ${ANSWER} ]]; then
            ANSWER=' '
        fi
        CHARACTERISTIC_INFORMATION_ANSWERS+=( "${ANSWER}" )
    done
    
    print "Appuyez sur entrée pour valider la saisie, ou N pour recommencer"
    ABORT=
    read ABORT
    if [[ $ABORT ]]; then
        ask_for_characteristic_informations
    else
        print_to_uc_file "# CHARACTERISTIC_INFORMATION"
        for index in ${!CHARACTERISTIC_INFORMATION[@]}; do
            print_to_uc_file "***${CHARACTERISTIC_INFORMATION[$index]}*** ${CHARACTERISTIC_INFORMATION_ANSWERS[$index]}"
        done
        print_to_uc_file "<hr>"
    fi
    
}
################################################################################
3_ask_for_main_success_scenario() {
    print "Saisissez ici les étapes du scénario nominal, une par une, laissez vide pour quitter la saisie :"
    step_counter=1
    print_to_uc_file "# MAIN SUCCESS SCENARIO"
    while :; do
        print "Step ${step_counter} :"
        current_step=
        read current_step
        if [[ -z ${current_step} ]]; then
            print "Fin de la saisie du scénario nominal"
            break
        fi
        step="* step #${step_counter}: ${current_step}"
        print_to_uc_file "${step}"
        step_counter=$(( $step_counter + 1 ))
    done
    print_to_uc_file "<hr>"

}

################################################################################


4_ask_for_extensions() {
    print "Saisir ici un par un les numéros de step soumis à extension, laissez vide pour quitter la saisie :"
    echo -e "${BLUE_STYLE}Les extensions sont les steps dans un UC qui sont décrits dans un UC dédié${RAZ_STYLE}"
    print_to_uc_file "# EXTENSIONS"
    while :; do
        print "Entrez le numéro de step à étendre :"
        current_step=
        read current_step
        if [[ -z ${current_step} ]]; then
            print "Fin de la saisie des extensions"
            break
        fi
        step="step altered #${current_step}"
        ls ./markdown
        print "Saisissez un libellé de UC détaillant l'extension s'il existe, ou un nom d'UC à créer plus tard (TODO à la place du numéro) :"
        read reference_extension
        step="* ***${step}*** > ${reference_extension}"
        print_to_uc_file "${step}"
    done
    print_to_uc_file "<hr>"

}


################################################################################

5_ask_for_sub_variation() {
    
    print_to_uc_file "# SUB-VARIATIONS"
    print "Saisissez ici les sous variations du scénario nominal (exemple 'payer par carte OU par chèque', ou 'l'acheteur n'a pas d'argent', ou 'l'acheteur a déjà le produit, allez à #NUM_STEP'), une par une, laissez vide pour quitter la saisie :"
    
    while :; do
        print "Entrez le numéro de step à sous découper :"
        current_step=
        read current_step
        if [[ -z ${current_step} ]]; then
            print "Fin de la saisie des sous-variations"
            break
        fi
        step="step: ${current_step}"
        print_to_uc_file "* ***step#${step} [SOUS-VARIATION]***"
        step_counter=1
        # On saisit ici les sous-steps
        while :; do
            print "Sub-step ${step_counter} :"
            current_sub_step=1
            read current_sub_step
            if [[ -z ${current_sub_step} ]]; then
                print "Fin de la saisie de la sous-variations du step #${current_step}" 
                break
            fi
            step="* step #${step_counter}: ${current_sub_step}"
            TRIPLE_SPACE='   '
            print_to_uc_file "${TRIPLE_SPACE}${step}"
            step_counter=$(( $step_counter + 1 ))
        done
    done
    print_to_uc_file "<hr>"
    
}

print_template() {
    print_separator
    print "Ce template est issue du travail d'Alistair Cockburn, à l'origine également de travaux sur l'agilité et le développement objets autour des années 2000, ouvrages qui ont influencé nos pratiques actuelles de travail de manière conséquente"
    print_separator
    cat ./resources/template.md
    print_separator
}





