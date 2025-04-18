import os

# Create __init__.py files for all directories to make them proper Python packages
directories = [
    "/home/ubuntu/AnkiForge/agents",
    "/home/ubuntu/AnkiForge/integrations",
    "/home/ubuntu/AnkiForge/utils",
    "/home/ubuntu/AnkiForge/config"
]

for directory in directories:
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Package initialization file\n")
        print(f"Created {init_file}")
    else:
        print(f"{init_file} already exists")
