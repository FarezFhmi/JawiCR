# 🧠 JawiCR

**Jawi Character Recognition** is a web-based application developed as part of a Final Year Project. It aims to recognize individual Jawi characters from images using a Convolutional Neural Network (CNN). The system enables users to upload either a single character or a word image, processes the input, and returns predicted characters. It features a user-friendly interface with character segmentation and manual selection capabilities.

---

## 🎯 Project Overview

This project modernizes the recognition process of Jawi script by integrating image processing and deep learning. Users can interact with the web app to upload character or word images, and the system handles segmentation, prediction, and display of results. It serves both educational and practical use cases in recognizing traditional Jawi script.

---

## 🚀 Features

### 👤 User Interface
- **Single Character Prediction**: Upload a Jawi character image to receive a prediction.
- **Word Image Upload**: Upload a full Jawi word; system automatically segments it into characters.
- **Character Selection**: Users can manually choose segmented characters for recognition.

### 🧠 AI & Processing
- **CNN Model**: Trained Convolutional Neural Network to classify Jawi characters.
- **Image Segmentation**: Uses OpenCV to split word images into individual characters.

---

## 🧰 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript  
- **Backend**: Flask (Python)  
- **AI Model**: CNN (TensorFlow/Keras)  
- **Image Processing**: OpenCV, Pillow  
- **Database**: MySQL (via XAMPP)  
- **Environment**: XAMPP, Python Virtual Environment

---

## 🛠️ Installation & Setup

1. **Start Services**: Open XAMPP and start **Apache** and **MySQL**.
2. **Database Setup**:
   - Create a MySQL database named `jawi_db`.
   - Import the `jawi_db.sql` file (if provided) into your database.
3. **Project Setup**:
   - Place project files in your local directory.
   - (Optional) Create and activate a Python virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
4. **Run the App**:
   ```bash
   python app.py
    ```
   - Visit the app at
   http://localhost:5000

## 🔐 Test Functionality

- Upload a Jawi character image and get prediction.
- Upload a full Jawi word image and test character segmentation.
- Select segmented characters to test prediction individually.

## 🧠 Model Info
- Trained on a dataset of labeled Jawi characters.
- CNN architecture using TensorFlow/Keras.
- Accuracy depends on image clarity and character distinction.
- Word images are processed with OpenCV for character segmentation.

## 📈 Future Improvements

- Improve accuracy of segmentation on complex handwriting.
- Add data upload and model retraining feature.
- Implement user authentication to track prediction history.
- Deploy with a public-facing domain for real-time usage

## 🙋‍♂️ Author
Farez Fahmi
Final Year Project — Jawi Character Recognition System
