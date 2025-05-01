import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

required = ["pip", "pygame", "openai" , "pygame_gui"]

for pkg in required:
    install(pkg)

print("¡Librerías instaladas correctamente!")