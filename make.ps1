$workdir = $PSScriptRoot
cd $workdir
echo "$workdir"

pyinstaller --onefile hpt.py -y