import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import random
import os

class ImageModifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title('AnnaSlipper')
        self.root.geometry('800x1200')
        root.state('zoomed')
        self.file_path = None
        self.original_image = None
        self.display_image = None
        self.resize_var = tk.BooleanVar()
        self.modify_all_var = tk.BooleanVar()
        lbl_title = tk.Label(root, text='AnnaSlipper For Roblox', font=('Helvetica', 16, 'bold'))
        lbl_title.pack(pady=10)
        self.canvas = tk.Canvas(root, width=400, height=300, bg='#e0e0e0', relief='sunken', bd=2)
        self.canvas.pack(pady=10)
        self.lbl_preview = tk.Label(self.canvas, text='No Image Loaded', bg='#e0e0e0', fg='#555')
        self.lbl_preview.place(relx=0.5, rely=0.5, anchor='center')
        btn_select = tk.Button(root, text='Select Image', command=self.load_image, width=20, height=2)
        btn_select.pack(pady=5)
        frame_controls = tk.LabelFrame(root, text='Modification Settings', padx=10, pady=10)
        frame_controls.pack(pady=10, fill='x', padx=20)
        self.lbl_percent = tk.Label(frame_controls, text='Pixels to Change: 50%')
        self.lbl_percent.grid(row=0, column=0, columnspan=2, sticky='w')
        self.slider = ttk.Scale(frame_controls, from_=1, to=100, orient='horizontal', command=self.update_slider_label)
        self.slider.set(50)
        self.slider.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        self.chk_all = tk.Checkbutton(frame_controls, text='Modify 100% (All Pixels)', variable=self.modify_all_var, command=self.toggle_slider)
        self.chk_all.grid(row=2, column=0, sticky='w')
        tk.Label(frame_controls, text='Number of Copies:').grid(row=3, column=0, sticky='w', pady=5)
        self.ent_copies = tk.Entry(frame_controls, width=10)
        self.ent_copies.insert(0, '1')
        self.ent_copies.grid(row=3, column=1, sticky='w', pady=5)
        frame_resize = tk.LabelFrame(root, text='Output Size (Optional)', padx=10, pady=10)
        frame_resize.pack(pady=10, fill='x', padx=20)
        self.chk_resize = tk.Checkbutton(frame_resize, text='Resize Output Image', variable=self.resize_var, command=self.toggle_resize_inputs)
        self.chk_resize.grid(row=0, column=0, columnspan=4, sticky='w')
        tk.Label(frame_resize, text='Width:').grid(row=1, column=0, sticky='e', padx=5)
        self.ent_width = tk.Entry(frame_resize, width=10, state='disabled')
        self.ent_width.grid(row=1, column=1, sticky='w')
        tk.Label(frame_resize, text='Height:').grid(row=1, column=2, sticky='e', padx=5)
        self.ent_height = tk.Entry(frame_resize, width=10, state='disabled')
        self.ent_height.grid(row=1, column=3, sticky='w')
        self.btn_process = tk.Button(root, text='Process & Save Copies', command=self.process_image, bg='#4CAF50', fg='white', font=('Helvetica', 12, 'bold'), state='disabled')
        self.btn_process.pack(pady=15, fill='x', padx=20)
        self.status_var = tk.StringVar()
        self.status_var.set('Ready')
        lbl_status = tk.Label(root, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        lbl_status.pack(side='bottom', fill='x')

    def load_image(self):
        file_types = [('Image files', '*.jpg *.jpeg *.png *.bmp *.tiff')]
        path = filedialog.askopenfilename(title='Select an Image', filetypes=file_types)
        if path:
            self.file_path = path
            try:
                self.original_image = Image.open(path).convert('RGBA')
                preview_img = self.original_image.copy()
                preview_img.thumbnail((400, 300))
                self.display_image = ImageTk.PhotoImage(preview_img)
                self.lbl_preview.place_forget()
                self.canvas.create_image(200, 150, image=self.display_image, anchor='center')
                self.btn_process.config(state='normal')
                self.status_var.set(f'Loaded: {os.path.basename(path)}')
                self.ent_width.config(state='normal')
                self.ent_height.config(state='normal')
                self.ent_width.delete(0, tk.END)
                self.ent_height.delete(0, tk.END)
                self.ent_width.insert(0, self.original_image.width)
                self.ent_height.insert(0, self.original_image.height)
                if not self.resize_var.get():
                    self.ent_width.config(state='disabled')
                    self.ent_height.config(state='disabled')
                return
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load image:\n{e}')
            return None

    def update_slider_label(self, val):
        self.lbl_percent.config(text=f'Pixels to Change: {int(float(val))}%')

    def toggle_slider(self):
        if self.modify_all_var.get():
            self.slider.state(['disabled'])
            self.lbl_percent.config(text='Pixels to Change: 100%')
        return None

    def toggle_resize_inputs(self):
        state = 'normal' if self.resize_var.get() else 'disabled'
        self.ent_width.config(state=state)
        self.ent_height.config(state=state)

    def process_image(self):
        if not self.original_image:
            messagebox.showwarning('Warning', 'Please load an image first.')
        return None
if __name__ == '__main__':
    root = tk.Tk()
    app = ImageModifierApp(root)
    root.mainloop()
