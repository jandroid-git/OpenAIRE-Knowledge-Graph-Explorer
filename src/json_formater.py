import os


#Beachte das die benötigten Dateien nicht komprimiert vorliegen dürfen - im fall erst lokal entzippen



# Ordner mit den Originaldaten
input_folder = r"data\original_projects_data_april2025"
# Ordner für die bearbeiteten Daten
output_folder = r"data\cleaned_projects_data_april2025"

# Stelle sicher, dass der Zielordner existiert, falls nicht, erstelle ihn
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Gehe alle Dateien im Zielordner durch
for file_name in os.listdir(input_folder):
    if file_name.endswith('.json'):
        # Erstelle den vollständigen Pfad zur Datei
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)

        try:
            # Öffne die Eingabedatei und lese die Zeilen
            with open(input_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Entferne führende und abschließende Leerzeichen und Zeilenumbrüche
            lines = [line.rstrip() for line in lines]

            # Öffne die Ausgabedatei, um sie zu bearbeiten
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write("[\n")  # Setze [ am Anfang der Datei

                # Füge Komma für jede Zeile hinzu, die mit '{' beginnt (außer der letzten)
                for i, line in enumerate(lines):
                    if line.startswith("{"):
                        # Wenn es nicht die letzte Zeile ist, ein Komma hinzufügen
                        if i < len(lines) - 1 and lines[i + 1].startswith("{"):
                            file.write(line + ",\n")
                        else:
                            file.write(line + "\n")
                    else:
                        file.write(line + "\n")

                file.write("]")  # Setze ] am Ende der Datei
            print(f"Die Datei {file_name} wurde erfolgreich bearbeitet und gespeichert.")
        except Exception as e:
            print(f"Fehler beim Bearbeiten der Datei {file_name}: {e}")
