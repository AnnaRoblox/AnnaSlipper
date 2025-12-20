# source code
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import random
import os

class ImageModifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AnnaSlipper")
        self.root.geometry("800x600") # Default size
        root.state('zoomed') 

        # Variables
        self.file_path = None
        self.original_image = None
        self.display_image = None
        self.resize_var = tk.BooleanVar()
        self.modify_all_var = tk.BooleanVar()
        self.exclude_transparency_var = tk.BooleanVar()

        # --- Scrollable Layout Setup ---
        
        # 1. Main Container Frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # 2. Canvas for Scrolling
        self.main_canvas = tk.Canvas(self.main_frame)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # 3. Scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # 4. Configure Canvas
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_canvas.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        # 5. Scrollable Frame (The content holder)
        self.scrollable_frame = tk.Frame(self.main_canvas)
        
        # Create window inside canvas
        self.canvas_window_id = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Ensure scrollable frame expands to canvas width
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mousewheel scrolling
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- UI Elements (Parented to self.scrollable_frame) ---

        # 1. Header
        lbl_title = tk.Label(self.scrollable_frame, text="AnnaSlipper For Roblox", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=10)

        # 2. Image Preview Area (Renamed canvas to preview_canvas)
        self.preview_canvas = tk.Canvas(self.scrollable_frame, width=400, height=300, bg="#e0e0e0", relief="sunken", bd=2)
        self.preview_canvas.pack(pady=10)
        self.lbl_preview = tk.Label(self.preview_canvas, text="No Image Loaded", bg="#e0e0e0", fg="#555")
        self.lbl_preview.place(relx=0.5, rely=0.5, anchor="center")

        # 3. Select Button
        btn_select = tk.Button(self.scrollable_frame, text="Select Image", command=self.load_image, width=20, height=2)
        btn_select.pack(pady=5)

        # 4. Modification Settings Frame
        frame_controls = tk.LabelFrame(self.scrollable_frame, text="Modification Settings", padx=10, pady=10)
        frame_controls.pack(pady=10, fill="x", padx=20)

        # Slider for percentage
        self.lbl_percent = tk.Label(frame_controls, text="Pixels to Change: 50%")
        self.lbl_percent.grid(row=0, column=0, columnspan=2, sticky="w")

        self.slider = ttk.Scale(frame_controls, from_=1, to=100, orient="horizontal", command=self.update_slider_label)
        self.slider.set(50)
        self.slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Checkbox for "Modify All"
        self.chk_all = tk.Checkbutton(frame_controls, text="Modify 100% (All Pixels)", 
                                      variable=self.modify_all_var, command=self.toggle_slider)
        self.chk_all.grid(row=2, column=0, sticky="w")

        # Checkbox for "Exclude Transparent Pixels"
        self.chk_transparency = tk.Checkbutton(frame_controls, text="Exclude Transparent Pixels", 
                                               variable=self.exclude_transparency_var, command=self.toggle_transparency_slider)
        self.chk_transparency.grid(row=3, column=0, sticky="w")

        # Transparency Tolerance Slider
        self.lbl_tolerance = tk.Label(frame_controls, text="Alpha Threshold (0-255): 0", state="disabled")
        self.lbl_tolerance.grid(row=4, column=0, sticky="w", padx=20)
        
        self.slider_tolerance = ttk.Scale(frame_controls, from_=0, to=255, orient="horizontal", command=self.update_tolerance_label, state="disabled")
        self.slider_tolerance.set(0)
        self.slider_tolerance.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=5)

        # Copies Input
        tk.Label(frame_controls, text="Number of Copies:").grid(row=6, column=0, sticky="w", pady=5)
        self.ent_copies = tk.Entry(frame_controls, width=10)
        self.ent_copies.insert(0, "1") # Default to 1 copy
        self.ent_copies.grid(row=6, column=1, sticky="w", pady=5)


        # 5. Resize Settings Frame
        frame_resize = tk.LabelFrame(self.scrollable_frame, text="Output Size (Optional)", padx=10, pady=10)
        frame_resize.pack(pady=10, fill="x", padx=20)

        self.chk_resize = tk.Checkbutton(frame_resize, text="Resize Output Image", 
                                         variable=self.resize_var, command=self.toggle_resize_inputs)
        self.chk_resize.grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(frame_resize, text="Width:").grid(row=1, column=0, sticky="e", padx=5)
        self.ent_width = tk.Entry(frame_resize, width=10, state="disabled")
        self.ent_width.grid(row=1, column=1, sticky="w")

        tk.Label(frame_resize, text="Height:").grid(row=1, column=2, sticky="e", padx=5)
        self.ent_height = tk.Entry(frame_resize, width=10, state="disabled")
        self.ent_height.grid(row=1, column=3, sticky="w")

        # 6. Process Button
        self.btn_process = tk.Button(self.scrollable_frame, text="Process & Save Copies", command=self.process_image, 
                                     bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), state="disabled")
        self.btn_process.pack(pady=15, fill="x", padx=20)

        # Status Bar (Parented to root to stay visible)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        lbl_status = tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w")
        lbl_status.pack(side="bottom", fill="x")

    def _on_canvas_configure(self, event):
        # Update the scrollregion
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        # Resize the inner frame to match the canvas width
        self.main_canvas.itemconfig(self.canvas_window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_image(self):
        file_types = [("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        path = filedialog.askopenfilename(title="Select an Image", filetypes=file_types)
        
        if path:
            self.file_path = path
            try:
                # CRITICAL CHANGE: Use RGBA to preserve transparency
                self.original_image = Image.open(path).convert("RGBA")
                
                # Display preview (thumbnail)
                preview_img = self.original_image.copy()
                preview_img.thumbnail((400, 300))
                self.display_image = ImageTk.PhotoImage(preview_img)
                
                # Clear text placeholder and add image
                self.lbl_preview.place_forget()
                # Update to use preview_canvas
                self.preview_canvas.create_image(200, 150, image=self.display_image, anchor="center")
                
                self.btn_process.config(state="normal")
                self.status_var.set(f"Loaded: {os.path.basename(path)}")
                
                # Pre-fill dimensions
                self.ent_width.config(state="normal")
                self.ent_height.config(state="normal")
                self.ent_width.delete(0, tk.END)
                self.ent_height.delete(0, tk.END)
                self.ent_width.insert(0, self.original_image.width)
                self.ent_height.insert(0, self.original_image.height)
                if not self.resize_var.get():
                    self.ent_width.config(state="disabled")
                    self.ent_height.config(state="disabled")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def update_slider_label(self, val):
        self.lbl_percent.config(text=f"Pixels to Change: {int(float(val))}")

    def toggle_slider(self):
        if self.modify_all_var.get():
            self.slider.state(["disabled"])
            self.lbl_percent.config(text="Pixels to Change: 100%")
        else:
            self.slider.state(["!disabled"])
            self.update_slider_label(self.slider.get())

    def toggle_resize_inputs(self):
        state = "normal" if self.resize_var.get() else "disabled"
        self.ent_width.config(state=state)
        self.ent_height.config(state=state)

    def update_tolerance_label(self, val):
        self.lbl_tolerance.config(text=f"Alpha Threshold (0-255): {int(float(val))}")

    def toggle_transparency_slider(self):
        if self.exclude_transparency_var.get():
            self.lbl_tolerance.config(state="normal")
            self.slider_tolerance.state(["!disabled"])
        else:
            self.lbl_tolerance.config(state="disabled")
            self.slider_tolerance.state(["disabled"])

    def process_image(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "Please load an image first.")
            return

        try:
            num_copies = int(self.ent_copies.get())
            if num_copies <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of copies must be a positive whole number.")
            self.status_var.set("Error: Invalid number of copies")
            return
        
        # Determine the target save directory (Downloads/annaslipper)
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        save_dir = os.path.join(downloads_dir, 'annaslipper')
        
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directory '{save_dir}':\n{e}")
            self.status_var.set("Error: Directory creation failed")
            return

        base_filename = os.path.splitext(os.path.basename(self.file_path))[0]
        
        
        # --- Start Batch Processing Loop ---
        for i in range(1, num_copies + 1):
            self.status_var.set(f"Processing copy {i} of {num_copies}...")
            self.root.update_idletasks()
            
            # 1. Working copy from the original image
            img = self.original_image.copy()
            pixels = img.load()
            width, height = img.size

            # 2. Identify eligible pixels & Calculate Count
            valid_coords = None
            
            if self.exclude_transparency_var.get():
                # Alpha is index 3. We consider alpha > tolerance as not transparent.
                tolerance = int(self.slider_tolerance.get())
                valid_coords = [(x, y) for x in range(width) for y in range(height) if pixels[x, y][3] > tolerance]
                total_pixels = len(valid_coords)
            else:
                total_pixels = width * height

            if self.modify_all_var.get():
                target_count = total_pixels
            else:
                percent = self.slider.get() / 100
                target_count = int(total_pixels * percent)

            # 3. Generate coordinates to modify
            coords = []
            if self.exclude_transparency_var.get():
                if target_count >= total_pixels:
                     coords = valid_coords
                else:
                     coords = random.sample(valid_coords, target_count)
            else:
                # Standard behavior (includes transparent pixels)
                if self.modify_all_var.get() or target_count > (total_pixels * 0.8):
                    coords = [(x, y) for x in range(width) for y in range(height)]
                    if not self.modify_all_var.get():
                        random.shuffle(coords)
                        coords = coords[:target_count]
                else:
                    coords = set()
                    while len(coords) < target_count:
                        x = random.randint(0, width - 1)
                        y = random.randint(0, height - 1)
                        coords.add((x, y))

            # 4. Modify Pixels (LSB Modification)
            def tweak(val):
                # Change the value by -1 or 1 (LSB modification)
                change = random.choice([-1, 1])
                new_val = val + change
                # Ensure we don't go out of RGB bounds (0-255)
                return max(0, min(255, new_val))

            for x, y in coords:
                # CRITICAL CHANGE: Get R, G, B, and Alpha (a)
                r, g, b, a = pixels[x, y]
                
                # Apply the tweak ONLY to the color channels (R, G, B)
                new_r = tweak(r)
                new_g = tweak(g)
                new_b = tweak(b)
                
                # Keep the original alpha channel (a) unchanged
                pixels[x, y] = (new_r, new_g, new_b, a)

            # 5. Resize if requested
            if self.resize_var.get():
                try:
                    new_w = int(self.ent_width.get())
                    new_h = int(self.ent_height.get())
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                except ValueError:
                    messagebox.showerror("Error", "Width and Height must be whole numbers.")
                    self.status_var.set("Error: Invalid Dimensions")
                    return
            
            # 6. Save the modified image
            save_path = os.path.join(save_dir, f"{base_filename}_{i:01d}.png")
            try:
                # PNG is required to save the alpha channel/transparency
                img.save(save_path, format='PNG')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image {i}:\n{e}")
                self.status_var.set("Error: Save failed")
                return

        # --- Batch Processing Complete ---
        self.status_var.set(f"Done! {num_copies} images saved successfully.")
        messagebox.showinfo("Success", f"All {num_copies} copies saved to:\n{save_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageModifierApp(root)
    root.mainloop()
