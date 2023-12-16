# [Selan Bank E_KYC project]

## Version: 1.8
**Release Date: July 14, 2023**

This is the initial release of [Selan Bank E_KYC project], which includes the following features:

- Feature 1: Liveness
- Feature 2: Bills
- Feature 3: OCR
- Feature 4: Face Extraction

Please refer to the documentation or user guide for more information on how to use [Selan Bank E_KYC project].

## Usage
1. Install Python dependencies: `pip install -r requirements.txt`
2. Run the application: `python manage.py runserver`
3. Open your browser and navigate to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Chapter 1: API Details

URLs and details which are passing through the APIs

### Liveness
- Liveness home page: `https://epictechdev.com:50179/api/ekyc/<user_id>` (Port: 8001)
- Get video list: `https://epictechdev.com:50179/api/ekyc/video_path/` (Port: 8001)
- Download the video: `https://epictechdev.com:50179/api/ekyc/download/<user_id>` (Port: 8001)

### Bills
- API URL: `https://epictechdev.com:50193/bills` (Port: 5001)
- Methods: POST, GET
- Input method: Form data
  - `file` (value: file)
  - `UserID` (value: str)
  - `Doc_Type` (value: str)
    - `Doc_Type` can be one of the following: WTB, ETB, SLT, DLG

### OCR
- API URL: `https://epictechdev.com:50193/upload` (Port: 5001)
- Method: POST
- Input method: Form data
  - `file` (value: file)
  - `UserID` (value: str)
  - `Doc_Type` (value: str)
    - `Doc_Type` can be one of the following: NIC, PP, DRL

### Face Extraction
- API URL: `https://epictechdev.com:50194/recognize` (Port: 5002)
- Methods: POST, GET
- Input method: Form data
  - `file` (value: doc_image)
  - `file` (value: selfie_image)

