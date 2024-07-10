import streamlit as st
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr
import os

# Function to clean up chunk files
def cleanup_chunks(num_chunks):
    if os.path.exists("audio_file.wav"):
        os.remove("audio_file.wav")
    # try: 
    if os.path.exists("uploaded_video.mp4"):
        os.remove("uploaded_video.mp4")
    for i in range(num_chunks):
        # print(i)
        chunk_name = f"chunk{i}.wav"
        if os.path.exists(chunk_name):
            os.remove(chunk_name)

    # except:
        # pass

# Custom CSS for responsiveness and animations
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .title {
        font-size: 2.5em;
        color: #4CAF50;
        text-align: center;
        animation: fadeIn 2s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    .upload-box {
        text-align: center;
        padding: 50px;
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        background-color: #ffffff;
        animation: slideIn 1.5s;
    }
    @keyframes slideIn {
        0% { transform: translateY(-50px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .result {
        margin-top: 20px;
        padding: 20px;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        background-color: #ffffff;
        animation: fadeIn 2s;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit app
st.markdown("<h1 class='title'>Video to Text Converter</h1>", unsafe_allow_html=True)

# File uploader
st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mkv", "avi", "mov"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    # Save uploaded file
    with open("uploaded_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("Processing video...")

    try:
        # Step 1: Extract audio from video
        video = mp.VideoFileClip("uploaded_video.mp4")
        audio_file = video.audio
        audio_file.write_audiofile("audio_file.wav")

        # Step 2: Split audio into smaller chunks
        audio = AudioSegment.from_file("audio_file.wav")
        chunk_length_ms = 60000  # 60 seconds
        chunks = make_chunks(audio, chunk_length_ms)

        # Step 3: Export chunks to separate files
        for i, chunk in enumerate(chunks):
            chunk_name = f"chunk{i}.wav"
            chunk.export(chunk_name, format="wav")

        # Step 4: Initialize recognizer
        r = sr.Recognizer()

        # Step 5: Process each chunk and display the text
        full_text = ""
        for i in range(len(chunks)):
            chunk_name = f"chunk{i}.wav"
            with sr.AudioFile(chunk_name) as source:
                data = r.record(source)
                try:
                    text = r.recognize_google(data)
                    full_text += text + " "
                except sr.RequestError as e:
                    st.error(f"Could not request results from Google Speech Recognition service; {e}")
                except sr.UnknownValueError:
                    st.warning("Google Speech Recognition could not understand the audio")

        st.markdown("<div class='result'>", unsafe_allow_html=True)
        st.write("The resultant text from the video is:")
        st.write(full_text)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Clean up chunk files and the extracted audio file
        try :
         cleanup_chunks(len(chunks))
        except:
            pass

# Run the Streamlit app
if __name__ == '__main__':
    st.write("Upload a video file to start.")
