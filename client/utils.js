

let websocket;
let context;
let processor;
let globalStream;
let isRecording = false;
let recordingSeconds = 0;
let is_conv_start = false;
let timerInterval = null;
let currentAnimation = null;



const websocketAddress = document.querySelector('#websocketAddress');
const selectedLanguage = document.querySelector('#languageSelect');
const websocketStatus = document.querySelector('#webSocketStatus');
const startButton = document.querySelector('#startButton');
startButton.disabled = false;

//const panel = document.querySelector('#silence_at_end_of_chunk_options_panel');
//const selectedStrategy = document.querySelector('#bufferingStrategySelect');
//const chunk_length_seconds = document.querySelector('#chunk_length_seconds');
//const chunk_offset_seconds = document.querySelector('#chunk_offset_seconds');
const audioPlayer = new Audio();
audioPlayer.style.display = "none";  // hide if added to DOM

// Optional: append to body so browser doesn't block autoplay on some devices
document.body.appendChild(audioPlayer);


function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.opacity = 1;

    setTimeout(() => {
        toast.style.opacity = 0;
    }, duration);
}







// function to play a audio file 

function playSound(audio_path) {
    
    const audio = new Audio(audio_path); 
    audio.play();

}







// Function to play audio from a URL without showing UI
function playAudioFromUrl(url) {

  try {
        audioPlayer.src = url;
      
         // Wait until audio is buffered enough
       audioPlayer.oncanplaythrough = () => {
         audioPlayer.play().then(() => {
         console.log("✅ Audio started playing...");
         loadAnimation("assets/agent_speaking.json",autoplay=true,is_current=true)
          audioPlayer.onended = () => {
            console.log("✅ Audio playback finished.");
            loadAnimation("assets/voice_animation.json", false, true);
            startButton.disabled = false;
            is_conv_start = false;
              };
           }).catch(err => {
        console.error("❌ Error playing audio:", err);
        loadAnimation("assets/voice_animation.json", false, true);
        startButton.disabled = false;
        is_conv_start = false;
      });
    };



               // If an error occurs
        audioPlayer.onerror = (e) => {
        console.error("❌ Error playing audio:", e);
        loadAnimation("assets/voice_animation.json",autoplay=false,is_current=true)
        startButton.disabled = false;
        is_conv_start = false
    

        reject(false);


        };


      } catch (err) {

        loadAnimation("assets/voice_animation.json",autoplay=false,is_current=true)
        console.error("Error playing audio:", err);
        startButton.disabled = false;
        is_conv_start = false


      }

    }


// 🔁 Timer function
function startTimer() {
    timerInterval = setInterval(() => {

        recordingSeconds++;
        console.log("recording seconds:-",recordingSeconds)

    }, 1000);
}



/// 🛑 To stop timer — call this when you stop recording

function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}




function resetWebsocketHandler() {
    if (isRecording) {
        stopRecordingHandler();
    }
    if (websocket.readyState === WebSocket.OPEN) {
        websocket.close();
    }
    
}



function connectWebsocketHandler() {
    if (!websocketAddress.value) {
        console.log("WebSocket address is required.");
        return;
    }




    websocket = new WebSocket(websocketAddress.value);
    websocket.onopen = () => {
        console.log("WebSocket connection established");
        showToast("🎙️ Agent started...");  
        websocketStatus.textContent = 'Connected';
    };




    websocket.onclose = event => {
        console.log("WebSocket connection closed", event);
        websocketStatus.textContent = 'Not Connected';
        startButton.disabled = false;
//        stopButton.disabled = true;
        
    };

    websocket.onmessage = event => {


       try {

        // Check if the data is a string
        if (typeof event.data === "string") {
            // Try parsing it as JSON
            const message = JSON.parse(event.data);
            // Handle different message types
            if (message.type === "process") {

                   console.log("conversations started....")
                   is_conv_start = true;
                   stopRecordingHandler();
                   loadAnimation("assets/progress.json",autoplay=true,is_current=true)


            } else if (message.type === "error") {

                loadAnimation("assets/voice_animation.json",autoplay=true,is_current=true)
                console.error(message.value);
                is_conv_start = false
                resetWebsocketHandler()
                playSound("assets/error_notific1.mp3")
                startButton.disabled = false;

            

            } else if (message.type === "url" && is_conv_start === true) {

                playAudioFromUrl(message.value);
                resetWebsocketHandler()

                return;

	  }else if (message.type ==="voice detected"){


              is_vad = true;


            } else {

                stopRecordingHandler();
                is_conv_start = false
                loadAnimation("assets/voice_animation.json",autoplay=true,is_current=true)
                console.warn("Unknown message type:", message.type);
                resetWebsocketHandler()


            }

            }



    } catch (err) {

        console.error("Failed to parse message:", err);
        console.log("Raw data:", event.data);
        is_conv_start = false
        stopRecordingHandler();
        loadAnimation("assets/voice_animation.json",autoplay=true,is_current=true)
        resetWebsocketHandler()
        playSound("assets/error_notific1.mp3")   
    }


    };


}





//function updateTranscription(transcript_data) {
//    if (Array.isArray(transcript_data.words) && transcript_data.words.length > 0) {
//        // Append words with color based on their probability
//        transcript_data.words.forEach(wordData => {
//
//            const span = document.createElement('span');
//            const probability = wordData.probability;
//            span.textContent = wordData.word + ' ';
//
//
//}



startButton.addEventListener("click", startRecordingHandler);




function startRecordingHandler() {
    if (isRecording) return;
    startButton.disabled = true;
    connectWebsocketHandler()

    // Wait a short delay to ensure WebSocket is connected before starting recording
    setTimeout(() => {
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            console.error("WebSocket not connected. Cannot start recording.");
            playSound("assets/error_notific1.mp3");
            showToast(" 😕 Agent not available...");
            return;
        }
    showToast("🎙️ Agent Listenting..."); 
    playSound("assets/start_notific.mp3")
    isRecording = true;
    is_conv_start = false
    recordingSeconds = 0; // ⏱ Reset the timer
    startTimer();         // 🔁 Start timer
    currentAnimation.play();


    context = new AudioContext();



    let onSuccess = async (stream) => {
        // Push user config to server
//        let language = selectedLanguage.value !== 'multilingual' ? selectedLanguage.value : null;
        sendAudioConfig("english");

        globalStream = stream;
        const input = context.createMediaStreamSource(stream);

         // ✅ Setup AnalyserNode
        const analyser = context.createAnalyser();
        analyser.fftSize = 2048;
        const frequencyData = new Uint8Array(analyser.frequencyBinCount);
        input.connect(analyser); // Connect mic to analyser

          // ⬇️ Make available to processAudio()
        window.analyser = analyser;
        window.frequencyData = frequencyData;


        const recordingNode = await setupRecordingWorkletNode();
        recordingNode.port.onmessage = (event) => {


        // ➕ Check dominant frequency before processing
            const dominantFreq = getDominantFrequency(context.sampleRate);
            const threshold = 10; // Hz (set your own value)

             if (dominantFreq > threshold) {
                processAudio(event.data); // Only send if freq > threshold
            }


        };
        input.connect(recordingNode);
    };
    let onError = (error) => {
        console.error(error);
    };
    navigator.mediaDevices.getUserMedia({
        audio: {
            echoCancellation: true,
            autoGainControl: false,
            noiseSuppression: true,
            latency: 0
        }
    }).then(onSuccess, onError);

    
//    stopButton.disabled = false;
 }, 1000); // adjust delay as needed
}


async function setupRecordingWorkletNode() {
    await context.audioWorklet.addModule('realtime-audio-processor.js');

    return new AudioWorkletNode(
        context,
        'realtime-audio-processor'
    );
}



// stopButton.addEventListener("click", stopRecordingHandler);


function stopRecordingHandler() {

    if (!isRecording) return;
    playSound("assets/end_notific.mp3")
    isRecording = false;
    recordingSeconds = 0;
    stopTimer()
    is_vad = false
    showToast("🎙️ Recording stopped...");


    if (globalStream) {
        globalStream.getTracks().forEach(track => track.stop());
    }
    if (processor) {
        processor.disconnect();
        processor = null;
    }

    if (context) {

        context.close().then(() => context = null);
    }




//    startButton.disabled = false;
//    stopButton.disabled = true;
}

function sendAudioConfig(language) {
    let processingArgs = {};

        processingArgs = {
            chunk_length_seconds: parseFloat(3),
            chunk_offset_seconds: parseFloat(0.1)
        };


    const audioConfig = {
        type: 'config',
        data: {
            sampleRate: context.sampleRate,
            channels: 1,
            language: 'english',
            processing_strategy: "silence_at_end_of_chunk",
            processing_args: processingArgs
        }
    };

    websocket.send(JSON.stringify(audioConfig));
}



function getDominantFrequency(sampleRate) {
    window.analyser.getByteFrequencyData(window.frequencyData);

    let maxVal = -Infinity;
    let maxIndex = -1;
    for (let i = 0; i < window.frequencyData.length; i++) {
        if (window.frequencyData[i] > maxVal) {
            maxVal = window.frequencyData[i];
            maxIndex = i;
        }
    }

    const dominantFreq = maxIndex * sampleRate / window.analyser.fftSize;
    return dominantFreq;
}




function processAudio(sampleData) {
    // ASR (Automatic Speech Recognition) and VAD (Voice Activity Detection)
    // models typically require mono audio with a sampling rate of 16 kHz,
    // represented as a signed int16 array type.
    //
    // Implementing changes to the sampling rate using JavaScript can reduce
    // computational costs on the server.

        if(!is_conv_start && recordingSeconds==10){

             stopRecordingHandler();
             startButton.disabled = false;
             recordingSeconds=0;
             stopTimer()
             currentAnimation.stop();
             return;

        }


        try{

          const sample_rate = context.sampleRate;
          const outputSampleRate = 16000;
          const decreaseResultBuffer = decreaseSampleRate(sampleData, sample_rate, outputSampleRate);
          const audioData = convertFloat32ToInt16(decreaseResultBuffer);

              if (websocket && websocket.readyState === WebSocket.OPEN) {

              websocket.send(audioData);

        }

//        // ✅ Step 3: Convert and send
//        const audioData = convertFloat32ToInt16(downsampled);
//        if (websocket && websocket.readyState === WebSocket.OPEN) {
//            websocket.send(audioData);
//        }




        } catch (e) {

          console.error("context is null...");


        }

}







function decreaseSampleRate(buffer, inputSampleRate, outputSampleRate) {
    if (inputSampleRate < outputSampleRate) {
        console.error("Sample rate too small.");
        return;
    } else if (inputSampleRate === outputSampleRate) {
        return;
    }

    let sampleRateRatio = inputSampleRate / outputSampleRate;
    let newLength = Math.ceil(buffer.length / sampleRateRatio);
    let result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
        let nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
        let accum = 0, count = 0;
        for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
        }
        result[offsetResult] = accum / count;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return result;
}




function convertFloat32ToInt16(buffer) {
    let l = buffer.length;
    const buf = new Int16Array(l);
    while (l--) {
        buf[l] = Math.min(1, buffer[l]) * 0x7FFF;
    }
    return buf.buffer;
}



// Initialize WebSocket on page load
//  window.onload = initWebSocket;

function toggleBufferingStrategyPanel() {
    if (selectedStrategy.value === 'silence_at_end_of_chunk') {
        panel.classList.remove('hidden');
    } else {
        panel.classList.add('hidden');
    }
}



function loadAnimation(path,autoplay=false,is_current=false) {

    if (is_current) {
      currentAnimation.destroy();
    }

    currentAnimation = lottie.loadAnimation({
      container: document.getElementById('lottie-container'),
      renderer: 'svg',
      loop: true,
      autoplay: autoplay,
      path: path
    });
  }






// Optionally, load the first animation on page load
window.onload = () => {
    loadAnimation('assets/voice_animation.json',is_current=false);
    // Connect to WebSocket on app load
   


  };




