import os

def generate_requirements():
    # Update pip
    os.system('pip install --upgrade pip')  # Pip selbst aktualisieren
    os.system('pip list --outdated | cut -d " " -f1 | xargs -n1 pip install -U')
    # Writes resources.txt
    os.system('pip freeze > ./resources.txt')
    print("Updated resources.txt with the latest package versions.")

generate_requirements()