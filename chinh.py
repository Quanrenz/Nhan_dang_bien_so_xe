import sys  # Import thư viện sys để làm việc với hệ thống
import cv2  # Import thư viện OpenCV để xử lý hình ảnh và video
import os   # Import thư viện os để làm việc với hệ thống tệp tin và thư mục
from PyQt5.QtGui import QImage, QPixmap  # Import các lớp QImage và QPixmap từ thư viện PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextBrowser ,QMessageBox # Import các lớp và tiện ích giao diện từ PyQt5
from PyQt5 import uic  # Import hàm uic từ PyQt5 để tải giao diện từ tệp .ui
from PyQt5.QtCore import Qt  # Import các lớp và chức năng core từ PyQt5
from BienSoXeCam import *
import easyocr

# Khởi tạo lớp chính (main window) cho ứng dụng
class MainWindow(QMainWindow):

    # Constructor của lớp MainWindow
    def __init__(self):
        super().__init__()  # Gọi constructor của lớp cha QMainWindow
        uic.loadUi("License plate recognition.ui", self)  # Tải giao diện từ tệp .ui và áp dụng nó cho cửa sổ chính
        self.pushButton.clicked.connect(live)  # Kết nối nút pushButton với phương thức select_image
        self.pushButton_2.clicked.connect(self.select_image)

    def select_image(self):
        options = QFileDialog.Options()  # Tạo đối tượng options cho hộp thoại lựa chọn file
        options |= QFileDialog.DontUseNativeDialog  # Không sử dụng hộp thoại mặc định của hệ thống
        fileName, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh", "", "Image Files (*.jpg *.png *.jpeg *.bmp)", options=options)  # Mở hộp thoại để chọn ảnh

        if fileName:  # Nếu người dùng đã chọn ảnh
            img = cv2.imread(fileName)  # Đọc ảnh từ đường dẫn fileName bằng OpenCV

            if img is not None:  # Nếu việc đọc ảnh thành công
                height, width, channel = img.shape  # Lấy thông tin chiều cao, chiều rộng và số kênh màu của ảnh
                bytesPerLine = 3 * width  # Tính số byte mỗi dòng ảnh

                # Chuyển đổi ảnh từ OpenCV sang QImage
                qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)  # Tạo QPixmap từ QImage

                # Hiển thị ảnh lên label
                self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio))
                # self.lineEdit.setPixmap(pixmap.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio))
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cv2.imshow("Anh xam", gray)
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11,2)
                cv2.imshow("Anh nhi phan", thresh)
                contours,h = cv2.findContours(thresh,1,2)
                largest_rectangle = [0,0]
                # Tạo đường viền để theo dõi bien so
                for cnt in contours:
                    approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True), True)
                    if len(approx)==4:
                        area = cv2.contourArea(cnt)
                        if area > largest_rectangle[0]:
                            largest_rectangle = [cv2.contourArea(cnt), cnt, approx]
                x,y,w,h = cv2.boundingRect(largest_rectangle[1])

                image = img[y:y+h, x:x+w]
                cv2.drawContours(img, [largest_rectangle[1]],0, (0,255,0), 10)

                cropped = img[y:y+h, x:x+w]
                cv2.imshow("Bien so xe", img)
                cv2.drawContours(img, [largest_rectangle[1]], 0, (0,255,0), 18)

                #DOC HINH ANH CHUYEN THANH FILE TEXT
                pytesseract.pytesseract.tesseract_cmd = 'D:\Github\\tesseract.exe'
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (3,3), 0)
                thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                # cv2.imshow('Crop', thresh)
                
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
                opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                invert = 255 - opening
                data = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')

                cv2.imshow('Result', thresh)
                
                print("Bien so xe la:")
                print(data)
                reader = easyocr.Reader(lang_list=["vi"])
                image_end = image
                gray_image = cv2.cvtColor(image_end, cv2.COLOR_BGR2GRAY)
                results = reader.readtext(image_end)
                full_text = " ".join([result[1] for result in results])
                print(f"Full Text: {full_text}")
                cv2.waitKey()
                cv2.waitKey(0)
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể đọc ảnh. Vui lòng chọn một tập tin hình ảnh hợp lệ.")
            
# Hàm chính của chương trình
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Tạo đối tượng ứng dụng QApplication
    mainWindow = MainWindow()  # Tạo đối tượng chính của ứng dụng MainWindow
    mainWindow.show()  # Hiển thị cửa sổ chính
    sys.exit(app.exec_())  # Khởi động ứng dụng và bắt đầu vòng lặp chính của ứng dụng
