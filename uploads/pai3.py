import cv2
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from pathlib import Path

class Interface:
    def __init__(self, root):
        self.lista = []
        self.root = root
        self.root.title("Menu")
        self.root.geometry("600x400")

        # Cria diretório 'uploads' 
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)

        self.button = tk.Button(self.root, text="Ler e visualizar imagens", command=self.add_task)
        self.button.pack(pady=5)
        self.button2 = tk.Button(self.root, text="Recortar ROIs", command=self.recortar_rois)
        self.button2.pack(pady=5)

        # Variáveis para a seleção de ROI
        self.roi_start = None
        self.roi_end = None

    def add_task(self):
        self.root2 = tk.Toplevel(self.root)
        self.root2.title("Ler e mostrar imagens")
        self.root2.geometry("600x400")

        self.label = tk.Label(self.root2, text="Título da tarefa:")
        self.label.pack(pady=0)

        self.button = tk.Button(self.root2, text="Upload", command=self.upload_image)
        self.button.pack(pady=5)
        self.button3 = tk.Button(self.root2, text="Mostrar Imagem", command=self.mostra_imagem)
        self.button3.pack(pady=10)

        self.button2 = tk.Button(self.root2, text="Voltar", command=self.voltar_add)
        self.button2.pack(pady=5)

    def mostra_imagem(self):
        self.root3 = tk.Toplevel(self.root)
        self.root3.title("Mostrar Imagem")
        self.root3.geometry("600x400")

        self.image_label = tk.Label(self.root3)
        self.image_label.pack(pady=20)

        self.select_button = tk.Button(self.root3, text="Selecionar Imagem", command=self.selecionar_imagem)
        self.select_button.pack(pady=5)

        self.image_files = list(self.uploads_dir.glob("*.png"))  
        self.image_index = 0

        if self.image_files:
            self.show_image()
            self.root3.bind("<Left>", self.previous_image)  
            self.root3.bind("<Right>", self.next_image)
        else:
            messagebox.showinfo("Informação", "Nenhuma imagem encontrada no diretório 'uploads'.")

    def show_image(self, image_path=None):
        if image_path:
            image = Image.open(image_path)
        elif self.image_files:
            image_path = self.image_files[self.image_index]
            image = Image.open(image_path)
        
        if image:
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.root3.title(f"Visualizando {Path(image_path).name}")
        else:
            messagebox.showinfo("Informação", "Nenhuma imagem encontrada.")

    def previous_image(self, event):
        if self.image_files and self.image_index > 0:
            self.image_index -= 1
            self.show_image()
        else:
            messagebox.showinfo("Fim da lista", "Você já está na primeira imagem.")

    def next_image(self, event):
        if self.image_files and self.image_index < len(self.image_files) - 1:
            self.image_index += 1
            self.show_image()

    def selecionar_imagem(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")],
            initialdir=self.uploads_dir
        )
        if file_path:
            self.show_image(image_path=file_path)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if not file_path:
            return

        #Salva a imagem em 'uploads'
        save_path = self.uploads_dir / Path(file_path).name
        image = Image.open(file_path)
        image.save(save_path)

        messagebox.showinfo("Sucesso", f"Imagem salva em: {save_path}")

    def recortar_rois(self):
        self.root4 = tk.Toplevel(self.root)
        self.root4.title("Recortar ROIs")
        self.root4.geometry("1000x600")

        self.image_label = tk.Label(self.root4)
        self.image_label.pack(pady=20)

        self.image_files = list(self.uploads_dir.glob("*.png"))
        self.image_index = 0 

        self.select_button = tk.Button(self.root4, text="Selecionar Imagem", command=self.selecionar_imagem_rois)
        self.select_button.pack(pady=5)

        if self.image_files:
            self.show_image_rois()
            self.root4.bind("<Left>", self.previous_image_rois)
            self.root4.bind("<Right>", self.next_image_rois)
        else:
            messagebox.showinfo("Informação", "Nenhuma imagem encontrada.")

        # Adiciona função de clique e arraste para selecionar a ROI
        self.root4.bind("<Button-1>", self.start_roi)
        self.root4.bind("<B1-Motion>", self.update_roi)
        self.root4.bind("<ButtonRelease-1>", self.save_roi)

    def start_roi(self, event):
        # Início da seleção da ROI
        self.roi_start = (event.x, event.y)

    def update_roi(self, event):
        # Atualiza o retângulo conforme o mouse é arrastado
        self.roi_end = (event.x, event.y)
        img_copy = self.image_label.image.copy()
        draw = ImageDraw.Draw(img_copy)
        draw.rectangle([self.roi_start, self.roi_end], outline="green", width=2)
        self.show_image_rois(image=img_copy)

    def save_roi(self, event):
        # Finaliza e salva a ROI
        if self.roi_start and self.roi_end:
            x1, y1 = self.roi_start
            x2, y2 = self.roi_end
            cropped_image = self.image_label.image.crop((x1, y1, x2, y2))

            # Salvar a ROI no diretório 'ROIs'
            roi_dir = Path("ROIs")
            roi_dir.mkdir(exist_ok=True)
            filename = f"ROI_{self.image_index}.png"
            cropped_image.save(roi_dir / filename)
            messagebox.showinfo("Sucesso", f"ROI salva como: {filename}")

    def show_image_rois(self, image_path=None, image=None):
        if image_path:
            image = Image.open(image_path)
        elif self.image_files:
            image_path = self.image_files[self.image_index]
            image = Image.open(image_path)
        
        if image:
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.root4.title(f"Visualizando {Path(image_path).name}")
        else:
            messagebox.showinfo("Informação", "Nenhuma imagem encontrada.")

    def previous_image_rois(self, event):
        if self.image_files and self.image_index > 0:
            self.image_index -= 1
            self.show_image_rois()
        else:
            messagebox.showinfo("Fim da lista", "Você já está na primeira imagem.")

    def next_image_rois(self, event):
        if self.image_files and self.image_index < len(self.image_files) - 1:
            self.image_index += 1
            self.show_image_rois()

    def selecionar_imagem_rois(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")],
            initialdir=self.uploads_dir
        )
        if file_path:
            self.show_image_rois(image_path=file_path)

    def voltar_add(self):
        self.root2.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()
