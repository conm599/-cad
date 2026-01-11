import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Optional, List
from image_processor import ImageProcessor, EdgeDetectionAlgorithm


class ImageToLineApp:
    def __init__(self):
        self.processor = ImageProcessor()
        self.current_image_path: Optional[str] = None
        self.processed_image: Optional[np.ndarray] = None
        self.batch_images: List[str] = []
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("图片转线条图工具")
        self.root.geometry("1200x800")
        
        self.setup_ui()
        
    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_main_area()
        
    def setup_sidebar(self):
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="图片转线条图",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.mode_frame = ctk.CTkFrame(self.sidebar)
        self.mode_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.mode_var = ctk.StringVar(value="single")
        self.single_mode_radio = ctk.CTkRadioButton(
            self.mode_frame,
            text="单张模式",
            variable=self.mode_var,
            value="single",
            command=self.on_mode_change
        )
        self.single_mode_radio.grid(row=0, column=0, padx=10, pady=5)
        
        self.batch_mode_radio = ctk.CTkRadioButton(
            self.mode_frame,
            text="批量模式",
            variable=self.mode_var,
            value="batch",
            command=self.on_mode_change
        )
        self.batch_mode_radio.grid(row=0, column=1, padx=10, pady=5)
        
        self.select_image_btn = ctk.CTkButton(
            self.sidebar,
            text="选择图片",
            command=self.select_image
        )
        self.select_image_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.algorithm_label = ctk.CTkLabel(
            self.sidebar,
            text="边缘检测算法",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.algorithm_label.grid(row=3, column=0, padx=20, pady=(20, 5))
        
        self.algorithm_combobox = ctk.CTkComboBox(
            self.sidebar,
            values=["Canny", "Sobel", "Prewitt", "Laplacian"],
            command=self.on_algorithm_change
        )
        self.algorithm_combobox.grid(row=4, column=0, padx=20, pady=5)
        self.algorithm_combobox.set("Canny")
        
        self.gaussian_label = ctk.CTkLabel(
            self.sidebar,
            text="高斯模糊核大小"
        )
        self.gaussian_label.grid(row=5, column=0, padx=20, pady=(15, 5))
        
        self.gaussian_slider = ctk.CTkSlider(
            self.sidebar,
            from_=1,
            to=15,
            number_of_steps=7,
            command=self.on_gaussian_change
        )
        self.gaussian_slider.grid(row=6, column=0, padx=20, pady=5)
        self.gaussian_slider.set(3)
        
        self.gaussian_value_label = ctk.CTkLabel(
            self.sidebar,
            text="3"
        )
        self.gaussian_value_label.grid(row=7, column=0, padx=20, pady=0)
        
        self.canny_frame = ctk.CTkFrame(self.sidebar)
        self.canny_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        
        self.canny_threshold1_label = ctk.CTkLabel(
            self.canny_frame,
            text="Canny 低阈值"
        )
        self.canny_threshold1_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.canny_threshold1_slider = ctk.CTkSlider(
            self.canny_frame,
            from_=0,
            to=255,
            command=self.on_canny_threshold1_change
        )
        self.canny_threshold1_slider.grid(row=1, column=0, padx=5, pady=5)
        self.canny_threshold1_slider.set(100)
        
        self.canny_threshold1_value = ctk.CTkLabel(
            self.canny_frame,
            text="100"
        )
        self.canny_threshold1_value.grid(row=2, column=0, padx=5, pady=0)
        
        self.canny_threshold2_label = ctk.CTkLabel(
            self.canny_frame,
            text="Canny 高阈值"
        )
        self.canny_threshold2_label.grid(row=3, column=0, padx=5, pady=5)
        
        self.canny_threshold2_slider = ctk.CTkSlider(
            self.canny_frame,
            from_=0,
            to=255,
            command=self.on_canny_threshold2_change
        )
        self.canny_threshold2_slider.grid(row=4, column=0, padx=5, pady=5)
        self.canny_threshold2_slider.set(200)
        
        self.canny_threshold2_value = ctk.CTkLabel(
            self.canny_frame,
            text="200"
        )
        self.canny_threshold2_value.grid(row=5, column=0, padx=5, pady=0)
        
        self.sobel_frame = ctk.CTkFrame(self.sidebar)
        self.sobel_label = ctk.CTkLabel(
            self.sobel_frame,
            text="Sobel/Laplacian 核大小"
        )
        self.sobel_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.sobel_slider = ctk.CTkSlider(
            self.sobel_frame,
            from_=1,
            to=7,
            number_of_steps=3,
            command=self.on_sobel_ksize_change
        )
        self.sobel_slider.grid(row=1, column=0, padx=5, pady=5)
        self.sobel_slider.set(3)
        
        self.sobel_value_label = ctk.CTkLabel(
            self.sobel_frame,
            text="3"
        )
        self.sobel_value_label.grid(row=2, column=0, padx=5, pady=0)
        
        self.invert_colors_var = ctk.BooleanVar(value=False)
        self.invert_colors_checkbox = ctk.CTkCheckBox(
            self.sidebar,
            text="反转颜色",
            variable=self.invert_colors_var,
            command=self.on_invert_change
        )
        self.invert_colors_checkbox.grid(row=9, column=0, padx=20, pady=10)
        
        self.save_btn = ctk.CTkButton(
            self.sidebar,
            text="保存图片",
            command=self.save_image
        )
        self.save_btn.grid(row=11, column=0, padx=20, pady=10)
        
        self.process_btn = ctk.CTkButton(
            self.sidebar,
            text="处理图片",
            command=self.process_image
        )
        self.process_btn.grid(row=12, column=0, padx=20, pady=10)
        
        self.update_algorithm_controls()
        
    def setup_main_area(self):
        self.image_info_label = ctk.CTkLabel(
            self.main_frame,
            text="请选择图片",
            font=ctk.CTkFont(size=12)
        )
        self.image_info_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="预览区域",
            font=ctk.CTkFont(size=20)
        )
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "single":
            self.select_image_btn.configure(text="选择图片")
        else:
            self.select_image_btn.configure(text="选择文件夹")
            
    def on_algorithm_change(self, choice):
        algorithm_map = {
            "Canny": EdgeDetectionAlgorithm.CANNY,
            "Sobel": EdgeDetectionAlgorithm.SOBEL,
            "Prewitt": EdgeDetectionAlgorithm.PREWITT,
            "Laplacian": EdgeDetectionAlgorithm.LAPLACIAN
        }
        self.processor.set_algorithm(algorithm_map[choice])
        self.update_algorithm_controls()
        if self.current_image_path:
            self.process_image()
            
    def update_algorithm_controls(self):
        algorithm = self.processor.current_algorithm
        
        if algorithm == EdgeDetectionAlgorithm.CANNY:
            self.canny_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
            self.sobel_frame.grid_forget()
        else:
            self.canny_frame.grid_forget()
            self.sobel_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
            
    def on_gaussian_change(self, value):
        kernel_size = int(value)
        if kernel_size % 2 == 0:
            kernel_size += 1
        self.processor.set_gaussian_blur_kernel(kernel_size)
        self.gaussian_value_label.configure(text=str(kernel_size))
        if self.current_image_path:
            self.process_image()
            
    def on_canny_threshold1_change(self, value):
        threshold1 = int(value)
        self.processor.set_canny_thresholds(threshold1, self.processor.canny_threshold2)
        self.canny_threshold1_value.configure(text=str(threshold1))
        if self.current_image_path:
            self.process_image()
            
    def on_canny_threshold2_change(self, value):
        threshold2 = int(value)
        self.processor.set_canny_thresholds(self.processor.canny_threshold1, threshold2)
        self.canny_threshold2_value.configure(text=str(threshold2))
        if self.current_image_path:
            self.process_image()
            
    def on_sobel_ksize_change(self, value):
        ksize = int(value)
        if ksize % 2 == 0:
            ksize += 1
        self.processor.set_sobel_ksize(ksize)
        self.processor.set_laplacian_ksize(ksize)
        self.sobel_value_label.configure(text=str(ksize))
        if self.current_image_path:
            self.process_image()
            
    def on_invert_change(self):
        if self.current_image_path:
            self.process_image()
            
    def select_image(self):
        mode = self.mode_var.get()
        
        if mode == "single":
            file_path = filedialog.askopenfilename(
                title="选择图片",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                self.current_image_path = file_path
                self.batch_images = []
                self.display_original_image()
                self.process_image()
        else:
            folder_path = filedialog.askdirectory(title="选择文件夹")
            if folder_path:
                import os
                from pathlib import Path
                
                self.batch_images = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']:
                    self.batch_images.extend(Path(folder_path).glob(ext))
                
                if self.batch_images:
                    self.current_image_path = str(self.batch_images[0])
                    self.image_info_label.configure(
                        text=f"已选择 {len(self.batch_images)} 张图片"
                    )
                    self.display_original_image()
                    self.process_image()
                else:
                    messagebox.showinfo("提示", "文件夹中没有找到图片文件")
                    
    def display_original_image(self):
        if self.current_image_path:
            image = self.processor.load_image(self.current_image_path)
            if image is not None:
                self.display_image(image)
                
    def display_image(self, cv_image):
        if len(cv_image.shape) == 2:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        else:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
        pil_image = Image.fromarray(cv_image)
        
        frame_width = self.image_frame.winfo_width()
        frame_height = self.image_frame.winfo_height()
        
        if frame_width > 1 and frame_height > 1:
            pil_image.thumbnail((frame_width - 20, frame_height - 20))
            
        tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.configure(image=tk_image, text="")
        self.image_label.image = tk_image
        
        if self.current_image_path:
            import os
            filename = os.path.basename(self.current_image_path)
            info = self.processor.get_image_info(self.current_image_path)
            if info:
                self.image_info_label.configure(
                    text=f"{filename} - 尺寸: {info[0]}x{info[1]}"
                )
                
    def process_image(self):
        if not self.current_image_path:
            return
            
        self.processed_image = self.processor.process_image(self.current_image_path)
        
        if self.processed_image is not None:
            if self.invert_colors_var.get():
                self.processed_image = self.processor.invert_colors(self.processed_image)
            self.display_image(self.processed_image)
            
    def save_image(self):
        if self.processed_image is None:
            messagebox.showwarning("警告", "请先处理图片")
            return
            
        mode = self.mode_var.get()
        
        if mode == "single":
            file_path = filedialog.asksaveasfilename(
                title="保存图片",
                defaultextension=".png",
                filetypes=[
                    ("PNG 图片", "*.png"),
                    ("JPEG 图片", "*.jpg"),
                    ("BMP 图片", "*.bmp"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                self.processor.save_image(self.processed_image, file_path)
                messagebox.showinfo("成功", "图片保存成功")
        else:
            self.batch_save_images()
            
    def batch_save_images(self):
        if not self.batch_images:
            messagebox.showwarning("警告", "请先选择图片文件夹")
            return
            
        output_folder = filedialog.askdirectory(title="选择保存文件夹")
        if not output_folder:
            return
            
        import os
        from pathlib import Path
        
        saved_count = 0
        failed_count = 0
        
        for image_path in self.batch_images:
            try:
                self.current_image_path = str(image_path)
                self.processed_image = self.processor.process_image(self.current_image_path)
                
                if self.processed_image is not None:
                    if self.invert_colors_var.get():
                        self.processed_image = self.processor.invert_colors(self.processed_image)
                    
                    filename = Path(image_path).stem
                    output_path = os.path.join(output_folder, f"{filename}_edges.png")
                    self.processor.save_image(self.processed_image, output_path)
                    saved_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                continue
                
        messagebox.showinfo(
            "批量处理完成",
            f"成功保存: {saved_count} 张\n失败: {failed_count} 张"
        )
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageToLineApp()
    app.run()
