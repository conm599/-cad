import cv2
import numpy as np
from enum import Enum
from typing import Optional, Tuple


class EdgeDetectionAlgorithm(Enum):
    CANNY = "Canny"
    SOBEL = "Sobel"
    PREWITT = "Prewitt"
    LAPLACIAN = "Laplacian"


class ImageProcessor:
    def __init__(self):
        self.current_algorithm = EdgeDetectionAlgorithm.CANNY
        self.gaussian_blur_kernel = 3
        self.canny_threshold1 = 100
        self.canny_threshold2 = 200
        self.sobel_ksize = 3
        self.laplacian_ksize = 3

    def set_algorithm(self, algorithm: EdgeDetectionAlgorithm):
        self.current_algorithm = algorithm

    def set_gaussian_blur_kernel(self, kernel_size: int):
        if kernel_size % 2 == 0:
            kernel_size += 1
        self.gaussian_blur_kernel = max(1, min(31, kernel_size))

    def set_canny_thresholds(self, threshold1: int, threshold2: int):
        self.canny_threshold1 = max(0, min(255, threshold1))
        self.canny_threshold2 = max(0, min(255, threshold2))

    def set_sobel_ksize(self, ksize: int):
        self.sobel_ksize = max(1, min(7, ksize))

    def set_laplacian_ksize(self, ksize: int):
        self.laplacian_ksize = max(1, min(7, ksize))

    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            import os
            nparr = np.fromfile(image_path, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return None
            return image
        except Exception:
            return None

    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def apply_gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        if self.gaussian_blur_kernel > 1:
            return cv2.GaussianBlur(image, (self.gaussian_blur_kernel, self.gaussian_blur_kernel), 0)
        return image

    def apply_canny(self, image: np.ndarray) -> np.ndarray:
        return cv2.Canny(image, self.canny_threshold1, self.canny_threshold2)

    def apply_sobel(self, image: np.ndarray) -> np.ndarray:
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=self.sobel_ksize)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=self.sobel_ksize)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sobel_magnitude = np.uint8(sobel_magnitude / sobel_magnitude.max() * 255)
        return sobel_magnitude

    def apply_prewitt(self, image: np.ndarray) -> np.ndarray:
        kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
        
        prewitt_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
        prewitt_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
        prewitt_magnitude = np.sqrt(prewitt_x**2 + prewitt_y**2)
        prewitt_magnitude = np.uint8(prewitt_magnitude / prewitt_magnitude.max() * 255)
        return prewitt_magnitude

    def apply_laplacian(self, image: np.ndarray) -> np.ndarray:
        laplacian = cv2.Laplacian(image, cv2.CV_64F, ksize=self.laplacian_ksize)
        laplacian = np.uint8(np.absolute(laplacian))
        return laplacian

    def process_image(self, image_path: str) -> Optional[np.ndarray]:
        image = self.load_image(image_path)
        if image is None:
            return None

        gray_image = self.convert_to_grayscale(image)
        blurred_image = self.apply_gaussian_blur(gray_image)

        if self.current_algorithm == EdgeDetectionAlgorithm.CANNY:
            edges = self.apply_canny(blurred_image)
        elif self.current_algorithm == EdgeDetectionAlgorithm.SOBEL:
            edges = self.apply_sobel(blurred_image)
        elif self.current_algorithm == EdgeDetectionAlgorithm.PREWITT:
            edges = self.apply_prewitt(blurred_image)
        elif self.current_algorithm == EdgeDetectionAlgorithm.LAPLACIAN:
            edges = self.apply_laplacian(blurred_image)
        else:
            edges = self.apply_canny(blurred_image)

        return edges

    def save_image(self, image: np.ndarray, output_path: str):
        try:
            ext = output_path.split('.')[-1].lower()
            ext_map = {
                'jpg': '.jpg',
                'jpeg': '.jpg',
                'png': '.png',
                'bmp': '.bmp',
                'tiff': '.tiff',
                'tif': '.tiff',
                'webp': '.webp'
            }
            ext = ext_map.get(ext, '.png')
            cv2.imencode(ext, image)[1].tofile(output_path)
        except Exception as e:
            print(f"保存图片失败: {e}")

    def invert_colors(self, image: np.ndarray) -> np.ndarray:
        return 255 - image

    def apply_threshold(self, image: np.ndarray, threshold: int = 127) -> np.ndarray:
        _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        return binary

    def get_image_info(self, image_path: str) -> Optional[Tuple[int, int, int]]:
        image = self.load_image(image_path)
        if image is None:
            return None
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        return (width, height, channels)
