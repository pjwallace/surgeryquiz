// Javascript for the quiz page
document.addEventListener('DOMContentLoaded', () =>{
    const viewResultsButton = document.getElementById('view-quiz-results');
    const cancelQuizScoreButton = document.getElementById('cancel-quiz-score-button');

    if (viewResultsButton){
        document.getElementById('view-quiz-results').addEventListener('click', () =>{
            displayQuizScoreDialog();
        });     
    }

    if (cancelQuizScoreButton){
        document.getElementById('cancel-quiz-score-button').addEventListener('click', () =>{
            cancelQuizScoreDialog();
        });    
    }   
});

function updateProgressBar(previousAnswers) {
    for (const [questionId, wasCorrect] of Object.entries(previousAnswers)) {
        const circle = document.getElementById(`circle-${questionId}`);
        const check = document.getElementById(`check-${questionId}`);
        const times = document.getElementById(`times-${questionId}`);

        if (circle) circle.style.display = 'none';

        if (wasCorrect === true || wasCorrect === 'true') {
            if (check) check.style.display = 'block';
            if (times) times.style.display = 'none';
        } else {
            if (check) check.style.display = 'none';
            if (times) times.style.display = 'block';
        }
    }
}

function highlightAnswers(resultsDict, questionType){    
    // loop over each key, value pair in resultsDict
    for (const [choice_id, result] of Object.entries(resultsDict)){
        const choiceElement = document.getElementById(`span-${choice_id}`);
        
        if (!choiceElement){
            continue;
        }

        // check if the choice was selected by the student
        if (result.selected_by_student){
            if (result.is_correct){
                choiceElement.style.backgroundColor = "rgba(0, 128, 0, 0.5)";
            }else{
                choiceElement.style.backgroundColor = "rgba(255, 0, 0, 0.5)";    
            }
        }else if(result.is_correct){
            // answer not selected by the student
            if (questionType === 'Multiple Answer'){
                choiceElement.style.backgroundColor = "yellow";
            }else{
                choiceElement.style.backgroundColor = "rgba(0, 128, 0, 0.5)";
            }
        }
    }
}

function formatAnsweredQuestion(studentAnswers){                    
    if (studentAnswers && studentAnswers.length > 0){
        // disable the submit button
        const submitButton = document.getElementById('submit-quiz-question');
        const viewQuizResults = document.getElementById('view-quiz-results');
        
        if (submitButton){
            submitButton.style.display = 'none';
        }

        // disable the view quiz results button                        
        if (viewQuizResults){
            viewQuizResults.style.display = 'none';
        } 
        
        // mark the choices selected by the student
        studentAnswers.forEach(choiceId=>{
            const choiceInput = document.querySelector(`input[type="checkbox"][value="${choiceId}"], input[type="radio"][value="${choiceId}"]`);
            
            if (choiceInput){
                choiceInput.checked = true;
            }
        });

        // disable all input boxes on the form
        const choiceInputs = document.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        choiceInputs.forEach(input => {
            input.disabled = true;
        });

    }
}

function displayQuizScoreDialog(){     
    const dialogElement = document.getElementById('quiz-score-dialog');

    if (dialogElement){        
        dialogElement.showModal();
    }else {
        console.error('Dialog element with ID quiz-score-dialog not found.');
        return; 
    }   
}

function cancelQuizScoreDialog(){
    const dialogElement = document.getElementById('quiz-score-dialog');

    if (dialogElement) {
        dialogElement.close();
    }
}

//function clearMessages(){
//
//     const messageContainer = document.querySelector('.error-msg');
//   const messageDiv = document.querySelector('.msg-div');
//    if (messageContainer) {
        // Clear any existing messages
//        messageContainer.innerHTML = '';
//    }
//    if (messageDiv) {
        // Clear any existing messages
//        messageDiv.innerHTML = '';
//    }
//}

