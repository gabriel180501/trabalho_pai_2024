import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path
import scipy.io
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage import img_as_ubyte

class Interface:
    def __init__(self, root):
        self.lista = []
        self.root = root
        self.root.title("Menu")
        self.root.geometry("600x400")

        self.imagem_original = None
        self.image_index = 0  #controla a imagem atual

        #Cria diretório 'uploads' 
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)

        self.button = tk.Button(self.root, text="Ler e visualizar imagens", command=self.add_task)
        self.button.pack(pady=5)
        self.button2 = tk.Button(self.root, text="Recortar ROIs", command=self.recortar_rois)
        self.button2.pack(pady=5)
        self.button3 = tk.Button(self.root, text="Calcular GLCM", command=self.calcular_glcm)
        self.button3.pack(pady=5)

        self.roi_start = None
        self.roi_end = None
        self.cropping = False
        self.image_files = list(self.uploads_dir.glob("*.png")) #Imagens na pasta

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

    def upload_image(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.mat")]
        )

        if self.file_path.endswith(".mat"):
            #Carrega dados do arquivo .mat
            data = scipy.io.loadmat(self.file_path)
            data_array = data['data']
            images = data_array['images']
            #imagem m do paciente n
            n = 1  #Índice do paciente
            m = 5  #Índice da imagem
            imagem = images[0][n][m]

            imagem_pil = Image.fromarray(imagem)

            save_path = self.uploads_dir / "imagem_salva.png"
            imagem_pil.save(save_path)

            self.imagem_original = imagem_pil
            self.image_files = list(self.uploads_dir.glob("*.png"))  #
            messagebox.showinfo("Sucesso", f"Imagem .mat carregada e salva como PNG em: {save_path}")
        else:
            if self.file_path:
                self.imagem_original = Image.open(self.file_path)
                save_path = self.uploads_dir / Path(self.file_path).name
                self.imagem_original.save(save_path)
                self.image_files = list(self.uploads_dir.glob("*.png"))  
                messagebox.showinfo("Sucesso", f"Imagem salva em: {save_path}")

    def mostra_imagem(self):
        if self.image_files:
            self.root3 = tk.Toplevel(self.root)
            self.root3.title("Mostrar Imagem")
            self.root3.geometry("600x400")

            self.image_label = tk.Label(self.root3)
            self.image_label.pack(pady=20)

            self.show_image()

            self.root3.bind("<Left>", self.previous_image)
            self.root3.bind("<Right>", self.next_image)
        else:
            messagebox.showinfo("Erro", "Nenhuma imagem encontrada na pasta uploads.")

    def show_image(self, image_path=None):
        if image_path:
            image = Image.open(image_path)
        else:
            image_path = self.image_files[self.image_index]
            image = Image.open(image_path)

        if image:
            self.imagem_original = image 
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
        else:
            messagebox.showinfo("Fim da lista", "Você já está na última imagem.")

    def recortar_rois(self):
        if self.image_files:  
            self.root4 = tk.Toplevel(self.root)
            self.root4.title("Recortar ROIs")
            self.root4.geometry("1000x600")

            self.image_label = tk.Label(self.root4)
            self.image_label.pack(pady=20)

            self.show_image_rois()  

           
            self.root4.bind("<Left>", self.previous_image_rois)
            self.root4.bind("<Right>", self.next_image_rois)

            self.image_label.bind("<Button-1>", self.start_roi)
            self.image_label.bind("<B1-Motion>", self.update_roi)
            self.image_label.bind("<ButtonRelease-1>", self.save_roi)
        else:
            messagebox.showinfo("Erro", "Nenhuma imagem encontrada na pasta uploads.")

    def show_image_rois(self, image_path=None):
        if image_path:
            self.imagem_original = Image.open(image_path) 
        else:
            image_path = self.image_files[self.image_index]
            self.imagem_original = Image.open(image_path)  

        if self.imagem_original:
            photo = ImageTk.PhotoImage(self.imagem_original)
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
        else:
            messagebox.showinfo("Fim da lista", "Você já está na última imagem.")

    def start_roi(self, event):
        self.roi_start = (event.x, event.y)
        self.cropping = True

    def update_roi(self, event):
        if self.cropping:
            self.roi_end = (event.x, event.y)
            img_copy = self.imagem_original.copy() 
            draw = ImageDraw.Draw(img_copy)

            draw.rectangle([self.roi_start, self.roi_end], outline="green", width=2)

            photo = ImageTk.PhotoImage(img_copy)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def save_roi(self, event):
        #salva a roi
        if self.roi_start and self.roi_end:
            x1, y1 = self.roi_start
            x2, y2 = self.roi_end
            cropped_image = self.imagem_original.crop((x1, y1, x2, y2))

            # Salvar a ROI no diretório 'ROIs'
            roi_dir = Path("ROIs")
            roi_dir.mkdir(exist_ok=True)  # Cria o diretório 'ROIs' se não existir
            filename = f"ROI_{self.image_index}_{self.roi_start[0]}_{self.roi_start[1]}.png"
            cropped_image.save(roi_dir / filename)
            messagebox.showinfo("Sucesso", f"ROI salva como: {filename}")
        self.cropping = False

    def calcular_glcm(self):
        if self.imagem_original:
            image_gray = self.imagem_original.convert("L")
            image_np = np.array(image_gray)
            image_np = img_as_ubyte(image_np)

            #define distancias radiais
            distances = [1, 2, 4, 8]
            angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

            glcm = graycomatrix(image_np, distances=distances, angles=angles, symmetric=True, normed=True)

            contrast = graycoprops(glcm, 'contrast')
            dissimilarity = graycoprops(glcm, 'dissimilarity')
            homogeneity = graycoprops(glcm, 'homogeneity')
            energy = graycoprops(glcm, 'energy')
            correlation = graycoprops(glcm, 'correlation')
            
            result_text = (
                f"GLCM Calculado para distâncias {distances}:\n"
                f"Contraste: {contrast}\n"
                f"Dissimilaridade: {dissimilarity}\n"
                f"Homogeneidade: {homogeneity}\n"
                f"Energia: {energy}\n"
                f"Correlação: {correlation}\n"
            )

            self.root5 = tk.Toplevel(self.root)
            self.root5.title("Resultados GLCM")
            self.root5.geometry("600x400")
            result_label = tk.Label(self.root5, text=result_text, justify="left")
            result_label.pack(pady=10)

        else:
            messagebox.showinfo("Erro", "Nenhuma imagem carregada para calcular a GLCM.")

    def voltar_add(self):
        self.root2.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()
