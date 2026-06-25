import gradio as gr
import sqlite3
import os
from pathlib import Path
from db.database import DBManager
import core.config as config
import logging

logger = logging.getLogger("UI")

# Custom CSS très poussé pour un look "Premium / Neo-morphism / Dark Mode"
custom_css = """
body {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #f1f5f9;
}
.gradio-container {
    max-width: 100% !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
}
.header-box {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    text-align: center;
    margin-bottom: 30px;
}
.header-box h1 {
    background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5em;
    font-weight: 800;
}
.gallery-container {
    background: rgba(15, 23, 42, 0.5);
    border-radius: 16px;
    padding: 15px;
    border: 1px solid rgba(148, 163, 184, 0.1);
}
.settings-box {
    background: rgba(30, 41, 59, 0.5);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.05);
}
.gr-button-primary {
    background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.6) !important;
}
#gallery {
    width: 100% !important;
    flex-grow: 1 !important;
}
#gallery .grid-wrap {
    width: 100% !important;
}
"""

class AdminApp:
    def __init__(self, db_manager: DBManager, rtsp_monitor=None):
        self.db = db_manager
        self.rtsp_monitor = rtsp_monitor

    def get_recent_visits(self):
        """Récupère les 20 dernières visites depuis la base de données pour la galerie."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, v.image_path, v.timestamp, c.name, c.id
            FROM Visits v
            JOIN Cats c ON v.cat_id = c.id
            ORDER BY v.timestamp DESC
            LIMIT 20
        ''')
        rows = cursor.fetchall()
        conn.close()
        from datetime import datetime, timezone
        gallery_items = []
        for row in rows:
            img_path = row[1]
            cat_name = row[3]
            utc_timestamp_str = row[2]
            
            # Conversion UTC vers Local Time pour l'affichage visuel
            try:
                utc_dt = datetime.strptime(utc_timestamp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                local_dt = utc_dt.astimezone()
                display_time = local_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                display_time = utc_timestamp_str
                
            if os.path.exists(img_path):
                # Format: (image_path, caption)
                gallery_items.append((img_path, f"{cat_name} - {display_time}"))
        
        return gallery_items, rows

    def update_settings(self, conf, cooldown):
        """Met à jour les paramètres et les sauvegarde sur le disque."""
        import core.config as config
        config.save_settings(conf / 100.0, cooldown)
        return f"Paramètres sauvegardés (et persistants) : Confiance={conf}%, Cooldown={cooldown} min."

    def apply_correction(self, visit_id, existing_name, new_name):
        if not visit_id:
            return "Veuillez sélectionner une image dans la galerie d'abord."
        
        final_name = new_name.strip() if new_name and new_name.strip() else existing_name
        if not final_name:
            return "Veuillez choisir ou écrire un nom valide."
            
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # 1. Récupérer les infos de la visite sélectionnée
        cursor.execute("SELECT cat_id, image_path FROM Visits WHERE id = ?", (visit_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "Erreur : visite introuvable."
            
        old_cat_id, image_path = row
        
        # 2. Récupérer le nom actuel du chat
        cursor.execute("SELECT name FROM Cats WHERE id = ?", (old_cat_id,))
        cat_row = cursor.fetchone()
        current_name = cat_row[0] if cat_row else ""
        
        if current_name.startswith("Nouveau_"):
            # Si l'IA n'avait pas reconnu le chat (profil "Nouveau"), 
            # on renomme simplement ce profil avec le bon nom !
            cursor.execute("UPDATE Cats SET name = ? WHERE id = ?", (final_name, old_cat_id))
            conn.commit()
            conn.close()
            return f"Profil temporaire renommé ! '{final_name}' a appris un nouveau visage."
        else:
            # Si l'IA s'était trompée en reconnaissant un chat DEJA CONNU (faux positif),
            # il ne faut SURTOUT PAS renommer le chat existant, sinon ça écrase le mauvais profil !
            # Il faut extraire le visage de cette photo et l'ajouter au BON chat.
            conn.close() # Fermer avant d'invoquer l'IA
            try:
                from PIL import Image
                from ai.reid import CatReID
                import logging
                logging.getLogger("ReID").setLevel(logging.ERROR) # Mute logs for quick extraction
                
                img = Image.open(image_path)
                reid = CatReID()
                new_embedding = reid.extract_features(img)
                
                # Créer une NOUVELLE entrée Cats (qui s'ajoutera au cluster de "final_name")
                new_cat_id = self.db.add_or_update_cat(final_name, new_embedding)
                
                # Mettre à jour la visite pour pointer vers ce nouveau vecteur
                conn2 = sqlite3.connect(self.db.db_path)
                c2 = conn2.cursor()
                c2.execute("UPDATE Visits SET cat_id = ? WHERE id = ?", (new_cat_id, visit_id))
                conn2.commit()
                conn2.close()
                return f"Faux positif corrigé ! L'IA a appris à quoi ressemble '{final_name}' sur cette photo spécifique."
            except Exception as e:
                return f"Erreur de traitement IA : {str(e)}"

    def build_ui(self):
        import core.config as config
        # Utilisation d'un thème sombre moderne fourni par Gradio, rehaussé par notre CSS
        self.theme = gr.themes.Monochrome(
            primary_hue="indigo",
            neutral_hue="slate",
            radius_size="lg",
            font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
        ).set(
            body_background_fill="var(--neutral-950)",
            body_text_color="var(--neutral-100)"
        )

        with gr.Blocks(title="PokeMinou Admin") as app:
            gallery_data = gr.State([])
            selected_visit_id = gr.State(None)
            
            with gr.Row(elem_classes="header-box"):
                gr.Markdown("# 🐾 PokeMinou Admin Dashboard\n*Système de Reconnaissance Faciale Féline*")

            with gr.Row():
                # Colonne Gauche : Paramètres
                with gr.Column(scale=1, elem_classes="settings-box"):
                    bridge_status_ui = gr.Markdown("Statut du Pont Eufy : 🔄 *Vérification...*")
                    gr.Markdown("---")
                    gr.Markdown("### ⚙️ Paramètres du Système")
                    conf_slider = gr.Slider(minimum=10, maximum=100, value=lambda: int(config.CONFIDENCE_THRESHOLD*100), step=5, label="Confiance YOLO (%)")
                    cooldown_slider = gr.Slider(minimum=1, maximum=60, value=lambda: config.COOLDOWN_MINUTES, step=1, label="Cooldown Notifications (minutes)")
                    save_btn = gr.Button("💾 Sauvegarder", variant="primary")
                    status_text = gr.Markdown("")
                    
                    save_btn.click(fn=self.update_settings, inputs=[conf_slider, cooldown_slider], outputs=status_text)
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🐈 Correction d'Identification")
                    selection_info = gr.Markdown("*Sélectionnez une image dans la galerie, puis choisissez le bon chat.*")
                    cat_list = [c["name"] for c in self.db.get_all_cats()]
                    cat_dropdown = gr.Dropdown(choices=cat_list, label="Identité Réelle")
                    new_cat_name = gr.Textbox(label="Ou créer un nouveau profil :")
                    correct_btn = gr.Button("✅ Appliquer la correction", variant="secondary")
                    correction_status = gr.Markdown("")
                    
                # Colonne Droite : Galerie
                with gr.Column(scale=3, elem_classes="gallery-container"):
                    gr.Markdown("### 📸 Dernières Visites")
                    refresh_btn = gr.Button("🔄 Rafraîchir la galerie")
                    gallery = gr.Gallery(
                        label="Images Recadrées", 
                        show_label=False, 
                        elem_id="gallery", 
                        columns=4, 
                        rows=3, 
                        height="85vh",
                        object_fit="contain"
                    )
                    
                    def refresh_ui():
                        items, rows = self.get_recent_visits()
                        # Mettre à jour la liste des chats
                        cats = [c["name"] for c in self.db.get_all_cats()]
                        
                        bridge_state = "🔴 **DÉCONNECTÉ** (Radar inactif)"
                        if self.rtsp_monitor and getattr(self.rtsp_monitor, 'is_running', False):
                            bridge_state = "🟢 **CONNECTÉ** (Radar RTSP en attente)"
                            
                        # Retourner les items pour la galerie, les raw data, le Dropdown mis à jour, et l'état du pont
                        return items, rows, gr.update(choices=list(set(cats))), f"Statut du Pont Eufy : {bridge_state}"
                        
                    def on_select(evt: gr.SelectData, rows):
                        index = evt.index
                        visit_id = rows[index][0]
                        cat_name = rows[index][3]
                        return visit_id, f"**Sélection actuelle :** Visite n°{visit_id} ({cat_name})"

                    app.load(fn=refresh_ui, outputs=[gallery, gallery_data, cat_dropdown, bridge_status_ui])
                    refresh_btn.click(fn=refresh_ui, outputs=[gallery, gallery_data, cat_dropdown, bridge_status_ui])
                    gallery.select(fn=on_select, inputs=[gallery_data], outputs=[selected_visit_id, selection_info])
                    correct_btn.click(
                        fn=self.apply_correction, 
                        inputs=[selected_visit_id, cat_dropdown, new_cat_name], 
                        outputs=correction_status
                    ).then(
                        fn=refresh_ui,
                        outputs=[gallery, gallery_data, cat_dropdown, bridge_status_ui]
                    )

        return app

def start_gradio(db_manager: DBManager, rtsp_monitor=None):
    """Point d'entrée pour lancer l'interface."""
    admin_app = AdminApp(db_manager, rtsp_monitor)
    app = admin_app.build_ui()
    # Lancement sur le port 8095
    logger.info("Démarrage de l'interface Gradio sur http://127.0.0.1:8095")
    app.launch(server_name="0.0.0.0", server_port=8095, prevent_thread_lock=True, theme=admin_app.theme, css=custom_css)
