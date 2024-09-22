import flet as ft
import requests
import os
import time

def main(page: ft.Page):
    page.title = "Remove Background App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file.value = e.files[0].name
            selected_file.update()
            remove_bg_button.disabled = False
            remove_bg_button.update()

    def remove_background(e):
        if selected_file.value:
            with open(pick_files_dialog.result.files[0].path, "rb") as file:
                response = requests.post("https://apitoflet.newposts.duckdns.org/remove-background/", files={"file": file})
            
            if response.status_code == 200:
                # Obtenir le nom de fichier pour l'export depuis les headers
                export_filename = response.headers.get('Export-Filename', 'image_sans_fond.png')
                
                # Générer un nom de fichier temporaire unique
                timestamp = int(time.time() * 1000)
                temp_file_path = f"temp_image_{timestamp}.png"
                
                # Sauvegarder temporairement l'image reçue
                with open(temp_file_path, "wb") as f:
                    f.write(response.content)
                
                # Mettre à jour l'image dans l'interface
                image.src = temp_file_path
                image.visible = True
                save_button.disabled = False
                
                # Stocker le nom de fichier pour l'export et le chemin temporaire
                remove_background.export_filename = export_filename
                remove_background.temp_file_path = temp_file_path
                
                # Supprimer l'ancienne image temporaire si elle existe
                if hasattr(remove_background, 'previous_temp_file'):
                    try:
                        os.remove(remove_background.previous_temp_file)
                    except:
                        pass
                remove_background.previous_temp_file = temp_file_path
                
                page.update()
            else:
                print("Erreur lors de la suppression de l'arrière-plan")

    def save_image(e):
        if hasattr(remove_background, 'export_filename') and hasattr(remove_background, 'temp_file_path'):
            save_file_dialog.save_file(file_name=remove_background.export_filename)

    def save_file_result(e: ft.FilePickerResultEvent):
        if e.path and hasattr(remove_background, 'temp_file_path'):
            os.rename(remove_background.temp_file_path, e.path)
            print(f"Image sauvegardée : {e.path}")
            # Réinitialiser le chemin du fichier temporaire après la sauvegarde
            remove_background.temp_file_path = None

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    save_file_dialog = ft.FilePicker(on_result=save_file_result)
    selected_file = ft.Text()

    page.overlay.extend([pick_files_dialog, save_file_dialog])

    image = ft.Image(visible=False, width=300, height=300, fit=ft.ImageFit.CONTAIN)

    remove_bg_button = ft.ElevatedButton("Supprimer l'arrière-plan", on_click=remove_background, disabled=True)
    save_button = ft.ElevatedButton("Sauvegarder l'image", on_click=save_image, disabled=True)

    page.add(
        ft.ElevatedButton(
            "Choisir une image",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False),
        ),
        selected_file,
        remove_bg_button,
        image,
        save_button
    )

ft.app(target=main)
