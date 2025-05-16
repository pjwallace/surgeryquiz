document.addEventListener('DOMContentLoaded', function(){
    const dashboardContainer = document.getElementById('dashboard-container');
    if (dashboardContainer){
        loadSubtopicsForQuizTopic();
    }
     
    // add eventlistener for a clicked retake button in the subtopics container
    document.getElementById('dashboard-container').addEventListener('click', function(e){
        const clickedButton = e.target.closest('button');
        if (!clickedButton) return;

        const subtopicId = clickedButton.dataset.subtopicId;
        if (!subtopicId) return;

        const topicId = clickedButton.dataset.topicId;
        if (!topicId) return;

        // process the retake button
        if (clickedButton.classList.contains('retake')){
            setupRetakeQuizDialog(subtopicId, topicId);
        } 
    });

    document.getElementById('confirm-quiz-retake-button').addEventListener('click', function(e) {
        e.preventDefault();  
        const href = this.href;  // Read the current href set by setupRetakeQuizDialog
        window.location.href = href;  // Navigate manually
    });
    
    document.getElementById('dashboard-container').addEventListener('click', function(e){
        if (e.target.tagName === 'BUTTON' && e.target.id === 'cancel-button'){
            cancelRetakeQuizDialog();
        }        
    });
}); 

function loadSubtopicsForQuizTopic(){
    document.getElementById('dashboard-container').addEventListener('click', function(e){           
            const topicDiv = e.target.closest('.topics');
            if (!topicDiv) return;

            e.preventDefault();

            const topicId = topicDiv.dataset.topicId;
            const subtopicsContainer = document.getElementById('subtopicscontainer-' + topicId);
            const plusIcon = document.getElementById('plus-' + topicId);
            const minusIcon = document.getElementById('minus-' + topicId);
            
            if (!subtopicsContainer || !plusIcon || !minusIcon) return;

            if (plusIcon.style.display === 'block'){
                subtopicsContainer.style.display = 'block';
                plusIcon.style.display = 'none';
                minusIcon.style.display = 'block';
            } else if (minusIcon.style.display === 'block'){
                subtopicsContainer.style.display = 'none';
                plusIcon.style.display = 'block';
                minusIcon.style.display = 'none';
            }             
    })          
}

function setupRetakeQuizDialog(subtopicId, topicId){
    const dialogElement = document.getElementById('confirm-retake-quiz-dialog');
    if (!dialogElement){
        console.error('Dialog element with ID confirm-retake-quiz-dialog not found.');
        return;
    }
    
    // set up the href link for the a tag
    const retakeLink = document.getElementById("confirm-quiz-retake-button");
    retakeLink.href = `/quizes/home/load_quiz_layout/${subtopicId}/${topicId}?button_type=retake`;
    dialogElement.showModal();
}

function cancelRetakeQuizDialog(){
    const dialogElement = document.getElementById('confirm-retake-quiz-dialog');
    if (!dialogElement){
        console.error('Dialog element with ID confirm-retake-quiz-dialog not found.');
        return;
    }
    dialogElement.close();
}
