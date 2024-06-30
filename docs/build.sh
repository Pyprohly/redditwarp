#!/bin/bash
print_usage() {
	cat <<EOF
Usage:
    prog full
    prog clean-all
EOF
}
do_build_main() { make html; }
do_build_apidoc() {
	pkg=./redditwarp
	[[ -d $pkg ]] || pkg=../redditwarp

	sphinx-apidoc -elf \
			-H "API Reference" \
			--tocfile=index \
			-t source/_templates/apidoc \
			-o generated/api \
			"$pkg"
}
do_clean_build() { make clean; }
do_clean_generated() {
	test -d generated/ || return 0
	echo "Removing everything under 'generated'..."
	rm -rf generated/*
}

if [[ $# -eq 0 || $1 == '--help' ]]
then
	print_usage
	exit 0
fi

for arg
do
	case $arg in
		main)
			do_build_main
			;;
		apidoc)
			do_build_apidoc
			;;
		full)
			do_build_apidoc
			do_build_main
			;;

		clean-build)
			do_clean_build
			;;
		clean-generated)
			do_clean_generated
			;;
		clean-all)
			do_clean_build
			do_clean_generated
			;;

		*)
			if [[ $arg == -* ]]
			then
				>&2 echo "Bad recipe name: $arg"
				exit 1
			fi

			make "$arg"
			;;
	esac
done
