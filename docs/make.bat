@echo off

if not defined SPHINXBUILD set SPHINXBUILD=sphinx-build
if not defined SPHINXOPTS set SPHINXOPTS=
set SOURCEDIR=source
set BUILDDIR=build

where "%SPHINXBUILD%" >nul 2>&1 || (
	echo(The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo(installed, then set the SPHINXBUILD environment variable to point
	echo(to the full path of the 'sphinx-build' executable. Alternatively you
	echo(may add the Sphinx directory to PATH.
	echo(
	echo(If you don't have Sphinx installed, grab it from
	echo(https://www.sphinx-doc.org/
	exit /b 1
)

if "%~1"=="" (
	"%SPHINXBUILD%" -M help %SPHINXOPTS% %O% _ _
	exit /b 0
)

:loop
"%SPHINXBUILD%" -M %1 %SPHINXOPTS% %O% "%SOURCEDIR%" "%BUILDDIR%"
if not "%~2"=="" shift & goto :loop
