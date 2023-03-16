@echo off
goto :main

:print_usage
	echo(Usage:
	echo(    prog full
	echo(    prog clean-all
exit /b

:do_build_main
	make html
exit /b

:do_build_apidoc
setlocal
	set pkg=./redditwarp
	if not exist "%pkg%\*" set pkg=../redditwarp

	sphinx-apidoc -ef ^
			-H "API Reference" ^
			--tocfile=index ^
			-t source/_templates/apidoc ^
			-o generated/api ^
			"%pkg%"
endlocal
exit /b

:do_clean_build
	make clean
exit /b

:do_clean_generated
	pushd generated || exit /b 0
	echo "Removing everything under 'generated'..."
	rm /s /q . 2>nul
	popd
exit /b

:main
set /a or = 0
if "%~1"=="" set /a or += 1
if "%~1"=="/?" set /a or += 1
if %or% gtr 0 (
	call :print_usage
	exit /b 0
)

:loop
if "%~1"=="main" (
	call :do_build_main
) else if "%~1"=="apidoc" (
	call :do_build_apidoc
) else if "%~1"=="full" (
	call :do_build_apidoc
	call :do_build_main

) else if "%~1"=="clean-build" (
	call :do_clean_build
) else if "%~1"=="clean-generated" (
	call :do_clean_generated
) else if "%~1"=="clean-all" (
	call :do_clean_build
	call :do_clean_generated

) else (
	setlocal EnableDelayedExpansion
	set "arg=%~1"
	if "!arg:~0,1!"=="-" (
		>&2 echo Bad recipe name: !arg!
		exit /b 1
	)
	endlocal

	make "%~1"
)
if not "%~2"=="" shift & goto :loop
