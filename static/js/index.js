// Helper functions

// Event listener for student drop down menu
const selectElement = document.querySelector('.select');
selectElement.addEventListener('change', function(event) {
    console.log(event);
    verifyFace(event);
});

// check if element is visible
function isVisible(element) {
    if (window.getComputedStyle(element).display === "block") {
        return true
      }
}

// function to send request to flask server
function sendRequest(url) {
    var flag = false;
    var requestPromise = fetch(url).then(function(response) {
        // error with request
        console.log(response.status)
        if (response.status != 200 && response.status != 500) {
            console.log('Looks like there was a problem. Status Code: ' + response.status);
            return "try again";
        // internal server error, probably best for users to start application again
        } else if (response.status == 500) {
            console.log("please restart");
            return "please restart";
        } else if (response.status == 200) {
            return response.json();
        }

    }).catch(function(err) {
        // error during fetch
        console.log('Looks like there is a problem with fetch: ', err);
        return "fetch error";
    });

    return requestPromise;
}

// sets a timeout
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// function for sliding through the slide elements
function slider() {
    var slideList = document.getElementsByClassName('slide')
    for (let i = 0; i < slideList.length; i++) {
        if (isVisible(slideList[i])) {
            var className = ".slide" + JSON.stringify(i + 1);
            $(className).animate({
                top: "-200",
                opacity: "0.2"
              }, 1500, function() {
                document.getElementsByClassName('slide')[i].style.display = "none";
                document.getElementsByClassName('slide')[i + 1].style.display = "block";
              });
        }
    }
}

// attach slider function to slide buttons
var nextButtons = document.getElementsByClassName('nextButton');
Array.from(nextButtons).forEach(function(element) {
    element.addEventListener('click', slider);
});

// function for shutting down the program
function shutdownServer() {
    window.location.href = "http://closekiosk";
    sendRequest('http://localhost:5000/shutdown').then(function(data) {
    });
}

// funciton for restarting after registration
function restart() {
    window.location.href = "http://localhost:5000";
}

// declare student variable
var student = "";


// slide 3

// function for if register button is pressed
async function register() {
    $('.registerButton').animate({
        opacity: "0"
    }, { duration: 2000, queue: false });
    $('.nextButton3').animate({
        opacity: "0"
    }, { duration: 2000, queue: false }, function() {
        document.getElementsByClassName('registerButton')[0].style.display = "none";
        document.getElementsByClassName('nextButton3')[0].style.display = "none";
    });

    await sleep(2000);

    document.getElementById('registerForm').style.display = "block";
}

// function for submitting the register form, POST request to server
function submitForm() {
    $('#student').animate({
        opacity: "0"
    }, { duration: 2000, queue: false });
    $('#file-label').animate({
        opacity: "0"
    }, { duration: 2000, queue: false });
    $('#submit').animate({
        opacity: "0"
    }, { duration: 2000, queue: false }, function() {
        document.getElementById('student').style.display = "none";
        document.getElementById('file-label').style.display = "none";
        document.getElementById('submit').style.display = "none";
    });

    var timeoutPromise = sleep(2000);
    timeoutPromise.then(function() {
        document.getElementsByClassName('load3')[0].style.display = "block";

        let data = new FormData();
        console.log($('input[type=text]')[0].value);
        console.log($('input[type=file]')[0].files[0]);
        data.append('name', $('input[type=text]')[0].value)
        data.append('image', $('input[type=file]')[0].files[0]);

        fetch('http://localhost:5000/register', {
            method: 'post',
            body: data,
        }).then(function (response) {
            return response.text();
        }).then(function (text) {
            document.getElementsByClassName('load3')[0].style.display = "none";
            document.getElementsByClassName('nextButtonRegister')[0].style.display = "block";
            console.log(text);
        }).catch(function (error) {
            console.log(error)
        });
    });

    // prevents page from reloading
    return false;
}

// slide 4

// function for if verify pc cam is pressed, GET request -> server
function verifyPCCam() {
    $('.verifyPCCamButton').animate({
        left: "16%"
    }, 1000, function() {
        document.getElementsByClassName('load4')[0].style.display = "block";
        document.getElementsByClassName('error4')[0].style.display = "none";
    });

    sendRequest('http://localhost:5000/verify_pc_cam').then(function(data) {
        console.log(data);
        document.getElementsByClassName('load4')[0].style.display = "none";
        if (data == "please restart") {
            document.getElementsByClassName('error4')[0].innerHTML = "Error: Please check your PC camera and restart the program";
            document.getElementsByClassName('verifyPCCamButton')[0].style.display = "none";
            document.getElementsByClassName('shutdown4')[0].style.display = "block";
        } else if (data == "try again") {
            document.getElementsByClassName('error4')[0].innerHTML = "Error: Please check your PC camera/internet connection and try again";
        } else {
            document.getElementsByClassName('nextButton4')[0].style.display = "block";
        }
    });
}

// slide 5

// function for if verify phone cam is pressed, sends GET request to server
function verifyPhoneCam() {
    $('.verifyPhoneCamButton').animate({
        left: "16%"
    }, 1000, function() {
        document.getElementsByClassName('load5')[0].style.display = "block";
        document.getElementsByClassName('error5')[0].style.display = "none";
    });

    sendRequest('http://localhost:5000/verify_phone_cam').then(function(data) {
        console.log(data);
        document.getElementsByClassName('load5')[0].style.display = "none";
        if (data == "please restart") {
            document.getElementsByClassName('error5')[0].innerHTML = "Error: Please check your phone camera and restart the program";
            document.getElementsByClassName('verifyPhoneCamButton')[0].style.display = "none";
            document.getElementsByClassName('shutdown5')[0].style.display = "block";
        } else if (data == "try again") {
            document.getElementsByClassName('error5')[0].innerHTML = "Error: Please check your Phone camera/internet connection and try again";
        } else {
            document.getElementsByClassName('nextButton5')[0].style.display = "block";
        }
    });
}

// slide 6

// function for if verify face buton is pressed, sends GET request to server
async function verifyFace(event) {
    $('#student-select').animate({
        left: "16%"
    }, 1000, function() {
        document.getElementsByClassName('load6')[0].style.display = "block";
        document.getElementsByClassName('error6')[0].style.display = "none";
    });

    student = event.target.value
    console.log(typeof(student));
    await sleep(1000);

    sendRequest('http://localhost:5000/verify_face').then(function(data) {
        console.log(data)
        var count = 0;
        document.getElementsByClassName('load6')[0].style.display = "none";
        if (data == "please restart") {
            document.getElementsByClassName('error6')[0].innerHTML = "Error: Please check your PC camera and restart the program";
            document.getElementById('student-select').style.display = "none";
            document.getElementsByClassName('shutdown6')[0].style.display = "block";
        } else if (data == "try again") {
            document.getElementsByClassName('error6')[0].innerHTML = "Error: Please check your Phone camera/internet connection and try again";
        } else {
            for (let i = 0; i < data.length; i++) {
                if (data[i][0].replace(/_/g," ") == student) {
                    document.getElementsByClassName('nextButton6')[0].style.display ="block";
                } else {
                    count += 1;
                }
            }

            if (count == data.length) {
                document.getElementById('student-select').value = "Test Student";
                document.getElementsByClassName('error6')[0].innerHTML = "Error: Are you sure you clicked the right student? Please try again.";
            }
        }
    });
}


// slide 7

// function for if verify hands button is pressed, sends GET request to server
async function verifyHands() {
    $('.verifyHandsButton').animate({
        left: "16%"
    }, 1000, function() {
        document.getElementsByClassName('load7')[0].style.display = "block";
        document.getElementsByClassName('error7')[0].style.display = "none";
    });

    await sleep(1000);

    sendRequest('http://localhost:5000/verify_hands').then(function(data) {
        var count = 0;
        console.log(data)
        document.getElementsByClassName('load7')[0].style.display = "none";
        if (data == "please restart") {
            document.getElementsByClassName('error7')[0].innerHTML = "Error: Please check your Phone camera and restart the program";
            document.getElementsByClassName('verifyHandsButton')[0].style.display = "none";
            document.getElementsByClassName('shutdown7')[0].style.display = "block";
        } else if (data == "try again") {
            document.getElementsByClassName('error7')[0].innerHTML = "Error: Please check your Phone camera/internet connection and try again";
        } else {
            for (let i = 0; i < data.length; i++) {
                if (data[i][0] == "hand") {
                    document.getElementsByClassName('nextButton7')[0].style.display ="block";
                    document.getElementById('subtext-audio').innerHTML = "press the button below and say: ' Hello my name is " + student + ", slowly and out loud' ";
                } else {
                    count += 1;
                }
            }

            if (count == data.length) {
                document.getElementsByClassName('error7')[0].innerHTML = "Error: Please make sure we can see your desk and hands and try again";
            }
        }
    });
}


// slide 8

//function for if verify audio button is pressed, sends GET request to server
async function verifyAudio() {
    $('.verifyAudioButton').animate({
        left: "16%"
    }, 1000, function() {
        document.getElementsByClassName('load8')[0].style.display = "block";
        document.getElementsByClassName('error8')[0].style.display = "none";
    });

    sendRequest('http://localhost:5000/verify_audio').then(function(data) {
        console.log(data);
        document.getElementsByClassName('load8')[0].style.display = "none";

        if (data == "please restart") {
            document.getElementsByClassName('error8')[0].innerHTML = "Error: Please check IP webcam app and restart the program";
            document.getElementsByClassName('verifyAudioButton')[0].style.display = "block";
            document.getElementsByClassName('shutdown8')[0].style.display = "block";
        } else if (data == "try again") {
            document.getElementsByClassName('error8')[0].innerHTML = "Error: Please check your IP webcam app/internet connection and try again";
        } else {
            if (data == "Audio okay") {
                document.getElementsByClassName('nextButton8')[0].style.display ="block";
                document.getElementsByClassName('error8')[0].innerHTML = "You have passed the verifications, you can now start the exam";

            } else {
                document.getElementsByClassName('error8')[0].innerHTML = "Error: Are you sure that your phone and pc are in the same room? Please try again";
            }
        }
    });
}

// slide 9

// function for if start exam button is pressed, starts the live timer and event log file stream
function startExam() {

    sendRequest('http://localhost:5000/start_exam?student=' + student.replace(/ /g,"_")).then(function(data) {
        if (data == "Exam started") {
            clockTimer(30, 'clock', "TIME IS UP");

            loadLogfile();
        }
    });
}

// function for displaying a live time (non-demo version: read duration of exam from school system)
async function clockTimer(seconds, element, message) {
    var endTime = new Date(Date.now() + seconds * 1000);
    var timer = setInterval(function() {
        var timeLeft = endTime.getTime() - Date.now();

        var hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        document.getElementById(element).innerHTML = "Time left: </br>" + hours + "H " + minutes + "M " + seconds + "S ";

        if (timeLeft < 0) {
            clearInterval(timer);
            document.getElementById(element).innerHTML = message;
            if (message == "Now collecting photos") {
                setTimeout(function() {
                    takePhoto();
                }, 2000);

            } else {
                slider();
                collectAnswers();
            }
        }

    }, 1000);
}

// function for displaying live update's of the camera listeners in a log file (demo-only)
function loadLogfile() {
    var logPromise = fetch('http://localhost:5000/logfile').then(function(response) {
        return response.text();
    });

    var timeOutPromise = sleep(10000);

    Promise.all([logPromise, timeOutPromise]).then(function(response) {
        console.log(response[0]);
        document.getElementsByClassName('logfileText')[0].innerHTML = response[0].replace("[", "").replace("]", "").replace("_", "\n");

        loadLogfile();
    });
}

// slide 10

// function for if collect Answers is pressed
function collectAnswers() {
    clockTimer(10, 'clock2', "Now collecting photos")
}

async function takePhoto() {
    sendRequest('http://localhost:5000/collect_answers').then(function(data) {
        console.log(data)
        if (data == "succesfull upload") {
            document.getElementById('endtitle').innerHTML = "That was it, great job " + student + "!"
            slider();
        }
    });
}

// slide 11

// function to close window
function closeWindow() {
    window.close();
}