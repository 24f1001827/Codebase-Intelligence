from app.ingestion.repository import discover_files

files = discover_files("C:/Users/Ashmit Ghose/Pricing Platform")

for file in files:
    print(file)