pyinstaller --onefile hpt.py -y
sys_arch=$(arch)
mv dist/hpt dist/hpt_$sys_arch
sudo cp dist/hpt_$sys_arch /usr/bin/hpt
sudo chmod +x /usr/bin/hpt
