# AI-VOICE-AGENT(AVA)


## 🚀 Installation Guide

Follow these steps to set up and run this project on your local machine.

**Clone the Repository**
```bash
git clone https://github.com/ak-123459/AVA.git
cd AVA
```

**Create and Activate a Virtual Environment(From Command line- Windows:)**
```
python -m venv PROJECT_AVA
PROJECT_AVA\Scripts\activate
```

**Create and Activate a Virtual Environment(From Command line- MacOS Linux:)**
```
python3 -m venv PROJECT_AVA
source PROJECT_AVA/bin/activate

```

**ADD .env file AND SECRETS**

```
HUGGINGFACE_TOKEN= YOUR_HUGGGING_FACE_TOKEN
NVIDIA_STT_API_KEY= YOUR_NVIDIA_NVC_API_KEY
MURF_TTS_API_KEY= YOUR_MURF_TTS_API_KEY
LLM_HOST_ENDPOINT= YOUR_CUSTOM_HOST_API_END_POINT
```


**Install Dependencies**

```
pip install -r requirements.txt
```

**Start websockets server**

```
python -m src.main
```

**Note:-** if permissions not given use sudo in linux.
eg.``sudo python -m src.main``


**Rurn the index.html file (Using python)**

```
cd client
python -m http.server 8001

```

***

## 🔧 Prerequisites

- Python >= 3.10
- pip (comes with Python)





