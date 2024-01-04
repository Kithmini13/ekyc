const video = document.getElementById('video');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const actions = ['Turn Left', 'Turn Right', 'Smile'];
const thresholdTurnRight = 3;
const thresholdTurnLeft = 3;
const thresholdSmile = 3;
let currentActionIndex = 0;
let timerInterval;
let turnRightCount = 0;
let turnLeftCount = 0;
let smileCount = 0;
let isStepCompleted = false;
let isTimerRunning = false;
let doesVideoNeedToSave = true;
let randomAction; // Declare randomAction variable
let mediaRecorder; // Declare mediaRecorder variable
let chunks = []; // Array to store video data chunks
let shouldSaveVideo = true;
const audioL = new Audio("/static/voice/left.mp3");
const audioR = new Audio("/static/voice/right.mp3");
const audioS = new Audio("/static/voice/smile.mp3");

const smilingThumbnailCanvas = document.createElement('canvas');
const smilingThumbnailContext = smilingThumbnailCanvas.getContext('2d');
let smiling_thumbnail;

let elapsedTimer = 0;
let currentAction = '';
let isFaceDetected = false;

const userId = userId2

const switchCameraButton = document.getElementById('switchCameraButton');
let currentCamera = 'environment'; // Default to the front (selfie) camera

function updateProgressBar(percentComplete) {
  progressBar.style.width = percentComplete + '%';
}

// Call this function to show the overlay and progress bar
function showProgressBar() {
  document.getElementById('progressOverlay').style.display = 'block';
  document.getElementById('progressContainer').style.display = 'block';
}

// Call this function to hide the overlay and progress bar
function hideProgressBar() {
  document.getElementById('progressOverlay').style.display = 'none';
  document.getElementById('progressContainer').style.display = 'none';
  document.getElementById('progressBar').style.display = 'none';
}


function playAudio(action) {
  switch (action) {
    case 'Turn Left':
      audioL.play();
      break;
    case 'Turn Right':
      audioR.play();
      break;
    case 'Smile':
      audioS.play();

      setTimeout(function () {
        smilingThumbnailCanvas.width = video.videoWidth;
        smilingThumbnailCanvas.height = video.videoHeight;
        smilingThumbnailContext.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        smiling_thumbnail = smilingThumbnailCanvas.toDataURL('image/jpeg'); // Store the snapshot as a data URL

        const thumbnailData = atob(smiling_thumbnail.split(',')[1]);
        const uint8Array = new Uint8Array(Array.from(thumbnailData).map((char) => char.charCodeAt(0)));

        const thumbnailBlob = new Blob([uint8Array], { type: 'image/jpeg' });

        saveImage(thumbnailBlob, userId);

        function saveImage(thumbnailBlob, userId) {
          var csrftoken = getCookie('csrftoken');
          const formData = new FormData();
          formData.append('image', thumbnailBlob); // Do not specify the filename here
          formData.append('user_id', userId); // Add user_id to the formData

          fetch('https://devekyc.seylan.lk:1003/api/ekyc/save_image/', {
            method: 'POST',
            headers: {
              'X-CSRFToken': csrftoken,
            },
            body: formData,
          })
            .then((response) => {
              if (response.ok) {
                console.log('Image saved successfully.');
              } else {
                console.error('Failed to save the image.');
              }
            })
            .catch((error) => {
              console.error('Error saving the image:', error);
            });
        }
      }, 3000);
      break;
    default:
      break;
  }
}

async function startVideo(camera) {
  try {
    if (video.srcObject) {
      // If a video stream is already active, stop it before switching cameras
      const stream = video.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach((track) => {
        track.stop();
      });
    }

    const constraints = {
      video: {
        facingMode: camera,
        width: { ideal: 854 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 },
      },
    };
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = stream;
    mediaRecorder = new MediaRecorder(stream);

    // Check if the camera is the selfie camera (user) and apply the transformation
    if (camera === 'environment') {
      video.style.transform = 'scaleX(1)';
    } else {
      video.style.transform = 'scaleX(-1)'; // Remove the transformation for the rear camera
    }

    video.srcObject = stream;
    mediaRecorder = new MediaRecorder(stream);
  } catch (err) {
    console.error(err);
  }
  doesVideoNeedToSave = true;
}

startVideo(currentCamera);

// Function to play the initial audio message
// function playAudioMessage() {
//   if (!isAudioPlayed) {
//     audioMessage.play();
//     isAudioPlayed = true;
//   }
// }

// Shuffles the array in place using Fisher-Yates algorithm
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri(staticURL + 'models'),
  faceapi.nets.faceLandmark68Net.loadFromUri(staticURL + 'models'),
  faceapi.nets.faceRecognitionNet.loadFromUri(staticURL + 'models'),
  faceapi.nets.faceExpressionNet.loadFromUri(staticURL + 'models'),
]).then(() => {
  console.log("Models Loaded");
  //shuffleArray(actions); // Shuffle the actions array
});

function getRandomAction() {
  return actions.splice(Math.floor(Math.random() * actions.length), 1)[0];
}

function displayAction(action) {
  const actionElement = document.getElementById('action');
  actionElement.innerText = action;

  if (action === 'Smile') {
    playAudio('Smile');
  } else if (action === 'Turn Left') {
    playAudio('Turn Left');
  } else if (action === 'Turn Right') {
    playAudio('Turn Right');
  }
}

function passResult(result) {
  // console.log(result);
}

function displayResult(result) {
  const resultElement = document.getElementById('verification');
  resultElement.innerText = result;
}

function displayTimer(time) {
  const timerElement = document.getElementById('timer');
  timerElement.innerText = time;
}

function resetCounters() {
  turnRightCount = 0;
  turnLeftCount = 0;
  smileCount = 0;
}

function stopVideo() {
  // Disable the "Switch Camera" button
  switchCameraButton.disabled = true;

  if (video.srcObject) {
    // If a video stream is active, stop it
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach((track) => {
      track.stop();
    });
  }
}

function startTimer(duration) {
  let timeRemaining = duration;
  const timerElement = document.getElementById('timer');

  timerInterval = setInterval(() => {
    timerElement.innerText = timeRemaining;

    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
      isStepCompleted = true; // Set the flag to indicate step completion
      return;
    }
    timeRemaining--;
  }, 1000);
}

function checkVerification() {
  let verificationResult = '';

  if (turnRightCount >= thresholdTurnRight && turnLeftCount >= thresholdTurnLeft && smileCount >= thresholdSmile) {
    verificationResult = 'SUCCESSFULL';
    passResult(verificationResult)
  } else {
    verificationResult = 'FAILED';
    displayResult('');
    passResult(verificationResult)
  }
  return verificationResult;
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

video.addEventListener('play', () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  document.body.append(canvas);

  // Set the canvas size to match the video element
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const displaySize = { width: video.videoWidth, height: video.videoHeight };
  faceapi.matchDimensions(canvas, displaySize);

  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function startNewAction() {
    clearInterval(timerInterval);
    randomAction = actions[currentActionIndex];

    await Promise.all([
      displayAction(randomAction),
      delay(2000).then(() => startTimer(3))
    ]);
  }

  function startProcess() {
    if (!isTimerRunning) {
      if (currentActionIndex >= actions.length) {
        // If all actions have been completed, stop the camera
        stopVideo();
        return;
      }
      if (elapsedTimer > 0 && currentAction) {
        // If there is an elapsed time and a current action, continue from where it stopped
        isTimerRunning = true;
        startTimer(3 - elapsedTimer); // Subtract the elapsed time from the total time
        displayAction(currentAction);
      } else {
        currentActionIndex = 0;
        isTimerRunning = true;
        isStepCompleted = false;
        shuffleArray(actions);
        startNewAction();
      }
      if (mediaRecorder.state === 'inactive') {
        mediaRecorder.start(); // Start recording when the process starts
        shouldSaveVideo = true;
      }
    }
  }

  function stopProcess() {
    shouldSaveVideo = false;
    timeRemaining = 0
    clearInterval(timerInterval);
    resetCounters();
    isStepCompleted = false;
    isTimerRunning = false;
    displayAction('');
    displayResult('');
    mediaRecorder.stop();
    // stopButton.disabled = true; // Disable the stop button
    // startButton.disabled = false;
    currentActionIndex = 0;
    shuffleArray(actions);
  }

  async function checkFaceDetection() {
    const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions({ inputSize: 128, scoreThreshold: 0.6, fastResize: true }));

    if (detections.length > 0) {
      // Start the process if a face is detected
      startProcess();
    }
  }

  // Periodically check for face detection and update the process
  const faceDetectionInterval = setInterval(checkFaceDetection, 100);


  setInterval(async () => {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions({ inputSize: 96, scoreThreshold: 0.3, fastResize: true }))
      .withFaceLandmarks()
      .withFaceExpressions();

    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    //faceapi.draw.drawFaceExpressions(canvas, resizedDetections);

    if (resizedDetections.length > 0) {
      const faceLandmarks = resizedDetections[0].landmarks._positions;
      const nose = faceLandmarks[30].x;

      // console.log('Nose position:', nose);

      const expressions = resizedDetections[0].expressions;
      const expressionThreshold = 0.5;

      if (expressions.happy > expressionThreshold) {
        if (randomAction === "Smile") {
          // console.log('Person is SMILING');
          smileCount++;
        }
      } else if (nose < 195) {
        if (randomAction === "Turn Right") {
          // console.log('Face turned to RIGHT');
          turnRightCount++;
        }

      } else if (nose > 240) {
        if (randomAction === "Turn Left") {
          // console.log('Face turned to LEFT');
          turnLeftCount++;
        }

      } else {
        // console.log('Face facing FORWARD');
        // console.log("------user id----", userId)
      }

      // Check if the current action is completed and move to the next action
      if (isTimerRunning && isStepCompleted) {
        isStepCompleted = false;
        currentActionIndex++; // Move to the next action

        if (currentActionIndex >= actions.length) {
          mediaRecorder.stop(); // Stop recording when the verification check is performed
          return;
        }
        startNewAction(); // Start the next action
      }
    } else {
      // console.log('No face to capture');
    }
  }, 100);

  // Event listener for recording data
  mediaRecorder.ondataavailable = function (event) {
    chunks.push(event.data);
  };

  // Event listener for when recording is stopped
  mediaRecorder.onstop = function () {
    // if (shouldSaveVideo) {
    //   const blob = new Blob(chunks, { type: 'video/mp4' });
    if (shouldSaveVideo) {
      const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

      let videoType;
      if (isSafari) {
        videoType = 'video/hevc';
      } else {
        videoType = 'video/mp4';
      }

      const blob = new Blob(chunks, { type: videoType });
      chunks = []; // Clear the chunks array for future recordings
      user = userId;
      // user = 'gagani3';
      // passDataToWebView(user);
      console.log('saveVideo not being called');
      if (doesVideoNeedToSave) {
        console.log('saveVideo called');
        showProgressBar();
        saveVideo(blob, user, timeout); // Call the function to save the recorded video
      }
      var pendingUrl = window.location.href + "#PENDING";
      window.history.pushState({}, "", pendingUrl);
      stopVideo();
    } else {
      chunks = []; // Clear the chunks array if the recording should not be saved
    }
  };

  function passResultToFlutter(result) {
    window.flutter_inappwebview.callHandler('resultHandler', result);
    // console.log('-----results-----', result)
  }

  function timeout() {
    const res = checkVerification();
    var newUrl = window.location.href + "?result=" + res;
    window.history.pushState({}, "", newUrl);
    displayResult(res);
    isTimerRunning = false;
    isStepCompleted = true; // Set isStepCompleted to true after displaying the result
    stopVideo();
  }

  function saveVideo(blob, userId, timeoutFunction, retryCount = 3) {
    var csrftoken = getCookie('csrftoken');
    const formData = new FormData();
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  
    let videoType;
    if (isSafari) {
      videoType = 'video/hevc';
    } else {
      videoType = 'video/mp4';
    }
  
    formData.append('video', blob, `recorded_video.${videoType.split('/')[1]}`);
    formData.append('user_id', userId);
  
    function sendRequest(retriesLeft) {
      const xhr = new XMLHttpRequest();
  
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          console.log(`Upload progress: ${percentComplete.toFixed(2)}%`);
          updateProgressBar(percentComplete);
        }
      });
  
      xhr.open('POST', 'https://devekyc.seylan.lk:1003/api/ekyc/save_video/');
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.timeout = 60000;
  
      xhr.onload = function () {
        console.clear();
        if (xhr.status === 200) {
          console.log('Video saved successfully.');
        } else {
          console.error('Failed to save the video.');
          if (retriesLeft > 0) {
            console.log(`Retrying... ${retriesLeft} attempts left.`);
            sendRequest(retriesLeft - 1);
          } else {
            console.log('All retries exhausted. Appending #ERROR to URL.');
            window.location.hash = 'ERROR';
          }
        }
  
        console.timeEnd('saveVideo');
        timeoutFunction();
        hideProgressBar();
      };
  
      xhr.onerror = function () {
        console.clear();
        console.error('Error saving the video.');
        if (retriesLeft > 0) {
          console.log(`Retrying... ${retriesLeft} attempts left.`);
          sendRequest(retriesLeft - 1);
        } else {
          console.log('All retries exhausted. Appending #ERROR to URL.');
          window.location.hash = 'ERROR';
        }
        timeoutFunction();
        hideProgressBar();
      };
  
      xhr.ontimeout = function () {
        console.clear();
        console.error('Request timed out.');
        if (retriesLeft > 0) {
          console.log(`Retrying... ${retriesLeft} attempts left.`);
          sendRequest(retriesLeft - 1);
        } else {
          console.log('All retries exhausted. Appending #ERROR to URL.');
          window.location.hash = 'ERROR';
        }
        timeoutFunction();
        hideProgressBar();
      };
  
      console.time('saveVideo');
      xhr.send(formData);
    }
  
    sendRequest(retryCount);
  }
  
});


switchCameraButton.addEventListener('click', () => {
  // Toggle between front and rear cameras
  currentCamera = currentCamera === 'user' ? 'environment' : 'user';

  if (currentCamera === 'user') {
    video.style.transform = 'scaleX(-1)';
  } else {
    video.style.transform = ''; // Remove the transformation for the rear camera
  }

  // Stop the existing timer and reset counters
  // hideProgressBar();
  isStepCompleted = false;
  isTimerRunning = false;
  resetCounters();

  clearInterval(timerInterval);
  displayAction('');
  displayResult('');
  displayTimer('');
  
  doesVideoNeedToSave = false;

  mediaRecorder = new MediaRecorder(video.srcObject);

  startVideo(currentCamera);
});


