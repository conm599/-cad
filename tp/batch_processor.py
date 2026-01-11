import os
from pathlib import Path
from typing import List, Callable, Optional
from image_processor import ImageProcessor, EdgeDetectionAlgorithm
import cv2
import numpy as np


class BatchProcessor:
    def __init__(self, processor: Optional[ImageProcessor] = None):
        self.processor = processor if processor else ImageProcessor()
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        self.progress_callback = callback
        
    def get_image_files(self, folder_path: str, extensions: Optional[List[str]] = None) -> List[str]:
        if extensions is None:
            extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
        
        image_files = []
        folder = Path(folder_path)
        
        for ext in extensions:
            image_files.extend(folder.glob(ext))
            image_files.extend(folder.glob(ext.upper()))
        
        return [str(f) for f in image_files]
    
    def process_single_image(
        self,
        input_path: str,
        output_path: str,
        invert_colors: bool = False
    ) -> bool:
        try:
            self.current_image_path = input_path
            processed_image = self.processor.process_image(input_path)
            
            if processed_image is None:
                return False
            
            if invert_colors:
                processed_image = self.processor.invert_colors(processed_image)
            
            self.processor.save_image(processed_image, output_path)
            return True
        except Exception as e:
            print(f"处理图片失败 {input_path}: {e}")
            return False
    
    def process_batch(
        self,
        input_folder: str,
        output_folder: str,
        output_format: str = "png",
        invert_colors: bool = False,
        suffix: str = "_edges"
    ) -> dict:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        image_files = self.get_image_files(input_folder)
        total = len(image_files)
        
        if total == 0:
            return {
                "success": 0,
                "failed": 0,
                "total": 0,
                "message": "没有找到图片文件"
            }
        
        success_count = 0
        failed_count = 0
        
        for idx, image_path in enumerate(image_files):
            if self.progress_callback:
                self.progress_callback(idx + 1, total, os.path.basename(image_path))
            
            try:
                filename = Path(image_path).stem
                output_path = os.path.join(
                    output_folder,
                    f"{filename}{suffix}.{output_format}"
                )
                
                if self.process_single_image(image_path, output_path, invert_colors):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"处理图片失败 {image_path}: {e}")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "message": f"批量处理完成: 成功 {success_count} 张, 失败 {failed_count} 张"
        }
    
    def process_batch_with_preview(
        self,
        image_files: List[str],
        output_folder: str,
        output_format: str = "png",
        invert_colors: bool = False,
        suffix: str = "_edges"
    ) -> dict:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        total = len(image_files)
        
        if total == 0:
            return {
                "success": 0,
                "failed": 0,
                "total": 0,
                "message": "没有图片需要处理"
            }
        
        success_count = 0
        failed_count = 0
        
        for idx, image_path in enumerate(image_files):
            if self.progress_callback:
                self.progress_callback(idx + 1, total, os.path.basename(image_path))
            
            try:
                filename = Path(image_path).stem
                output_path = os.path.join(
                    output_folder,
                    f"{filename}{suffix}.{output_format}"
                )
                
                if self.process_single_image(image_path, output_path, invert_colors):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"处理图片失败 {image_path}: {e}")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "message": f"批量处理完成: 成功 {success_count} 张, 失败 {failed_count} 张"
        }
    
    def get_processor(self) -> ImageProcessor:
        return self.processor
    
    def set_processor(self, processor: ImageProcessor):
        self.processor = processor


class BatchProcessorWithGUI:
    def __init__(self, processor: Optional[ImageProcessor] = None):
        self.batch_processor = BatchProcessor(processor)
        self.progress_window = None
        self.progress_bar = None
        self.progress_label = None
        self.cancel_button = None
        self.is_cancelled = False
        
    def process_with_progress_dialog(
        self,
        input_folder: str,
        output_folder: str,
        output_format: str = "png",
        invert_colors: bool = False,
        suffix: str = "_edges"
    ) -> dict:
        import customtkinter as ctk
        
        self.is_cancelled = False
        
        self.progress_window = ctk.CTkToplevel()
        self.progress_window.title("批量处理进度")
        self.progress_window.geometry("400x150")
        self.progress_window.resizable(False, False)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_window,
            text="准备处理..."
        )
        self.progress_label.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_window)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        
        self.cancel_button = ctk.CTkButton(
            self.progress_window,
            text="取消",
            command=self.cancel_processing
        )
        self.cancel_button.pack(pady=10)
        
        def progress_callback(current: int, total: int, filename: str):
            if self.is_cancelled:
                return
            
            progress = current / total
            self.progress_bar.set(progress)
            self.progress_label.configure(
                text=f"处理中: {current}/{total} - {filename}"
            )
            self.progress_window.update()
        
        self.batch_processor.set_progress_callback(progress_callback)
        
        def process_task():
            result = self.batch_processor.process_batch(
                input_folder,
                output_folder,
                output_format,
                invert_colors,
                suffix
            )
            
            if not self.is_cancelled:
                self.progress_bar.set(1)
                self.progress_label.configure(text=result["message"])
                self.cancel_button.configure(text="关闭", command=self.close_progress_window)
                self.progress_window.update()
        
        self.progress_window.after(100, process_task)
        
        return {}
    
    def cancel_processing(self):
        self.is_cancelled = True
        self.progress_label.configure(text="正在取消...")
        self.progress_window.update()
        
    def close_progress_window(self):
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None


def process_folder(
    input_folder: str,
    output_folder: str,
    algorithm: EdgeDetectionAlgorithm = EdgeDetectionAlgorithm.CANNY,
    canny_threshold1: int = 100,
    canny_threshold2: int = 200,
    gaussian_blur_kernel: int = 3,
    sobel_ksize: int = 3,
    invert_colors: bool = False,
    output_format: str = "png",
    suffix: str = "_edges"
) -> dict:
    processor = ImageProcessor()
    processor.set_algorithm(algorithm)
    processor.set_canny_thresholds(canny_threshold1, canny_threshold2)
    processor.set_gaussian_blur_kernel(gaussian_blur_kernel)
    processor.set_sobel_ksize(sobel_ksize)
    processor.set_laplacian_ksize(sobel_ksize)
    
    batch_processor = BatchProcessor(processor)
    return batch_processor.process_batch(
        input_folder,
        output_folder,
        output_format,
        invert_colors,
        suffix
    )


if __name__ == "__main__":
    result = process_folder(
        input_folder="input",
        output_folder="output",
        algorithm=EdgeDetectionAlgorithm.CANNY,
        canny_threshold1=100,
        canny_threshold2=200,
        gaussian_blur_kernel=3,
        invert_colors=True
    )
    print(result["message"])
