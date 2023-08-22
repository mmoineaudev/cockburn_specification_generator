#!/bin/bash

convert_all() {
    all_specifications=( 
        $(ls ./markdown/)
    )
    for specification in ${all_specifications[@]}; do
        convert_a_specification ${specification}
    done 

}

convert_a_specification() {
    target="$1"
    target_without_extension=${target//.md/}
    target_without_extension=${target_without_extension//markdown\//}
    print "lancement de la conversion : pandoc -o ./word/${target_without_extension}.docx -f markdown -t docx ${target}"
    pandoc -o ./word/${target_without_extension}.docx -f markdown -t docx ${target}
}