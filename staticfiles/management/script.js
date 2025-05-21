let confirmDeleteTopicModal = null;
let confirmDeleteSubtopicModal = null;


document.addEventListener('DOMContentLoaded', function(){
        
    initializePage();       
}); 

let currentOpenMenu = null; // keeps track of currently open sidebar menu

function initializePage(){
    // load subtopics for the chosen topic in the sidebar
    loadSuptopicsForTopic();

    // Display the instruction for the default question type (Multiple Choice)
    //selectQuestionType(true);
    const questionType = document.getElementById('question-type');
    if (questionType){
        selectQuestionType(true);
    }

    // display the appropriate database management instructions based on screen size
    const welcomeContainer = document.getElementById('welcome-container')
        if (welcomeContainer){
            changeWelcomeMessageBasedOnScreenSize();
        }

    window.addEventListener('resize', changeWelcomeMessageBasedOnScreenSize);

    // form submission event listeners
    document.getElementById('management-container').addEventListener('submit', function(e){
        // Ensure the event is coming from forms that are processed asynchronously
        if (e.target.getAttribute('data-fetch') === 'true') {
            e.preventDefault(); // Prevent the default form submission

            // add topic
            if (e.target.id === 'add-topic-form'){
                addTopic();
            }  
            
            // rename topic
            if (e.target.id === 'rename-topic-form'){
                renameTopic();
            }

            // add subtopic
            if (e.target.id === 'add-subtopic-form'){
                addSubtopic();
            }
            
            // rename subtopic
            if (e.target.id === 'rename-subtopic-form'){
                renameSubtopic();
            }

            // add question and choices
            if (e.target.id === 'add-question-and-choices-form'){
                addQuestionAndChoices();
            }

            // edit question and choices
            if (e.target.id === 'edit-question-form') {
                selectQuestionToEdit();
            }

            // submit edited question and choices
            if (e.target.id === 'edit-question-and-choices-form') {
                editQuestionAndChoices();
            }

            // submit add explanation
            if (e.target.id === 'add-explanation-form'){
                addExplanation();
            }

            // submit edit explanation
            if (e.target.id === 'edit-explanation-form'){
                editExplanation();
            }
        }              
           
    });

    // add event listener for dynamic loading of dropdown menus
    document.getElementById('management-container').addEventListener('change', function(e){
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-renamed-subtopic'){
            setupSelectSubtopicToRename();        
        }
        // after choosing a topic, load the subtopic menu
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-to-choose'){
            setupSelectSubtopicToDelete();        
        }
        // load the subtopic menu when adding a question
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-question'){
            setupSelectSubtopicsForQuestion();        
        }
        // retrieve the question type name when adding a question
        if (e.target.tagName === 'SELECT' && e.target.id === 'question-type'){
            selectQuestionType();      
        }
        // load the subtopic menu when editing a question
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-edit-question'){
            selectTopicForQuestionToEdit();        
        }
        // load the menu after selecting a subtopic when editing a question
        if (e.target.tagName === 'SELECT' && e.target.id === 'subtopic-for-edit-question'){
            const selectedSubtopicId = document.getElementById('subtopic-for-edit-question').value;
            loadQuestionsToEdit(selectedSubtopicId);        
        }
        // load the subtopic menu when editing all questions for a topic/subtopic
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-get-all-questions'){
            selectTopicForAllQuestionsToEdit();        
        }
        // load the subtopic menu when adding an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-add-explanation'){
            selectTopicForAddExplanation();        
        }
        // load the question menu when adding an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'subtopic-for-add-explanation'){
            loadQuestionsToAddExplanationForm();        
        }
        // load the answer choices when adding an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'question-for-add-explanation'){
            loadChoicesToAddExplanationForm();        
        }
        // load the subtopic menu when editing an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'topic-for-edit-explanation'){
            selectTopicForEditExplanation();        
        }
        // load the question menu when adding an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'subtopic-for-edit-explanation'){
            loadQuestionsToEditExplanationForm();        
        }
        // load the answer choices when adding an explanation
        if (e.target.tagName === 'SELECT' && e.target.id === 'question-for-edit-explanation'){
            loadChoicesToEditExplanationForm(); 
            getExplanationForQuestion();       
        }
    });

    
    // add event listener for dynamic click events (buttons other than 'submit')
    document.getElementById('management-container').addEventListener('click', function(e){
        // topic delete
        if (e.target.tagName === 'BUTTON' && e.target.id === 'delete-topic-btn'){
            confirmDeleteTopicModal = setupDeleteTopicModal();         
        }
        if (e.target.tagName === 'BUTTON' && e.target.id === 'confirm-delete-topic-button'){
            confirmTopicDeletion(confirmDeleteTopicModal);    
        }
        
        // subtopic delete
        if (e.target.tagName === 'BUTTON' && e.target.id === 'delete-subtopic-btn'){
            confirmDeleteSubtopicModal = setupDeleteSubtopicModal();         
        }
        if (e.target.tagName === 'BUTTON' && e.target.id === 'confirm-delete-subtopic-button'){
            confirmSubtopicDeletion(confirmDeleteSubtopicModal);    
        } 
        // add another choice to the add question and choices form
        if (e.target.tagName === 'BUTTON' && e.target.id === 'add-choice-btn'){
            addAnotherChoice();         
        }
        // add another choice to the edit question and choices form
        if (e.target.tagName === 'BUTTON' && e.target.id === 'add-choice-btn-edit'){
            addChoiceToEditForm();         
        } 
        // question delete dialog
        if (e.target.tagName === 'BUTTON' && e.target.id === 'delete-question-btn'){
            setupDeleteQuestionDialog();         
        }
        // cancel question delete dialog
        if (e.target.tagName === 'BUTTON' && e.target.id === 'cancel-button'){
            cancelQuestionDialog(); 
        }
        // delete question
        if (e.target.tagName === 'BUTTON' && e.target.id === 'confirm-delete-question-button'){
            deleteQuestion();    
        }
        // explanation delete dialog
        if (e.target.tagName === 'BUTTON' && e.target.id === 'delete-explanation-btn'){
            setupDeleteExplanationDialog();         
        }
        // cancel question delete dialog
        if (e.target.tagName === 'BUTTON' && e.target.id === 'cancel-delete-explanation-button'){
            cancelExplanationDialog(); 
        }
        // delete question
        if (e.target.tagName === 'BUTTON' && e.target.id === 'confirm-delete-explanation-button'){
            deleteExplanation();    
        }
    });
    
    // delete explanation
    //setupDeleteExplanationModal();

}

function loadSuptopicsForTopic(){
    // add event listener to each topic in the sidebar
    document.querySelectorAll('.topic').forEach(topicATag =>{
        topicATag.addEventListener('click', function(e){
            e.preventDefault();
            const topicId = topicATag.dataset.topicId;
            const subtopicsContainer = document.getElementById('subtopicscontainer-' + topicId);
            let downIcon = document.getElementById('caretdown-' + topicId);
            let upIcon = document.getElementById('caretup-' + topicId);
            
            // downIcon won't exist if there are no subtopics yet for the chosen topic
            if (!downIcon){
                downIcon = document.createElement('i');
                downIcon.classList.add('fa', 'fa-caret-down');
                downIcon.setAttribute('id', `caretdown-${topicId}`);
                downIcon.style.display = 'none';
            }
           
            // check if subtopics have already been loaded for the chosen topic
            if (subtopicsContainer.children.length > 0){
                subtopicsContainer.innerHTML = '';
                // hide the subtopics container and display the down caret
                if (subtopicsContainer.style.display === 'block'){
                    subtopicsContainer.style.display = 'none';
                    downIcon.style.display = 'block';
                    upIcon.style.display = 'none';
                    topicATag.appendChild(downIcon);
                }
               
            }else{
                // fetch subtopics for the chosen topic
                route = `/management/portal/subtopics_for_topic/${topicId}`;
                fetch(route)
                .then(response => response.json())
                .then(data =>{
                    if (data.success){
                        subtopicsContainer.innerHTML = '';
                        data.subtopics.forEach(subtopic =>{
                            const subtopicATag = document.createElement('a');
                            subtopicATag.setAttribute('href', '#');
                            subtopicATag.setAttribute('id', `subtopic-${subtopic.id}`);
                            subtopicATag.setAttribute('class', 'subtopic');
                            subtopicATag.setAttribute('data-subtopic-id', subtopic.id);
                            subtopicATag.textContent = subtopic.name;

                            // create a span for the question icon and badge.
                            // This will display the number of questions for each subtopic
                            const iconSpan = document.createElement('span');
                            iconSpan.setAttribute('class', 'icon-with-badge');

                            // create the question mark icon
                            const questionIcon = document.createElement('i');
                            questionIcon.setAttribute('class', 'fas fa-question-circle');

                            // Create the badge element to display the number of questions
                            const badge = document.createElement('span');
                            badge.setAttribute('class', 'badge');
                            badge.setAttribute('id', `badge-${subtopic.id}`);
                            badge.textContent = subtopic.question_count;

                            // Append the question icon and badge to the icon span
                            iconSpan.appendChild(questionIcon);
                            iconSpan.appendChild(badge);

                            // Append the icon span to the subtopic link
                            subtopicATag.appendChild(iconSpan);

                            // create the div to hold the sidebar menu options
                            const sidebarMenu = document.createElement('div');
                            sidebarMenu.setAttribute('class', 'sidebar-menu dropdown-menu');
                            sidebarMenu.setAttribute('id', 'sidebarmenu-${subtopic.id');

                            // initially the menu will not be displayed
                            sidebarMenu.style.display = 'none';

                            // add menu options
                            // add a question and answer choices
                            const addQuestionOption = document.createElement('a');
                            addQuestionOption.setAttribute('class', 'dropdown-item');
                            addQuestionOption.setAttribute('id', 'dropdown-add-question');
                            addQuestionOption.setAttribute('href', '#');
                            addQuestionOption.textContent = 'Add Question/Choices';

                            addQuestionOption.addEventListener('click', function(e) {
                                e.preventDefault();
                                addQuestion(topicId, subtopic.id);
                            });

                            // Display edit/review questions menu option if question count > 0
                            let badgeValue = parseInt(badge.textContent, 10);

                            // edit/delete a question
                            const editQuestionOption = document.createElement('a');
                            editQuestionOption.setAttribute('class', 'dropdown-item');
                            editQuestionOption.setAttribute('id', 'dropdown-edit-question');
                            editQuestionOption.setAttribute('href', '#');
                            editQuestionOption.textContent = 'Edit/Delete Question';

                            editQuestionOption.addEventListener('click', function(e) {
                                e.preventDefault();
                                getQuestionToEditFromSidebar(topicId, subtopic.id);
                            });
                                                        
                            sidebarMenu.appendChild(addQuestionOption);
                            
                            if (badgeValue > 0){
                                sidebarMenu.appendChild(editQuestionOption);
                            }                           

                            // Append the menu to the subtopic link
                            subtopicATag.appendChild(sidebarMenu);

                            // Add event listener to the subtopic link
                            subtopicATag.addEventListener('click', function(e) {
                                e.preventDefault();

                                 // Check if the clicked menu is the currently open menu
                                if (currentOpenMenu === sidebarMenu) {
                                    sidebarMenu.style.display = 'none';
                                    currentOpenMenu = null; // No menu is currently open
                                } else {
                                    // Hide all other submenus
                                    hideSidebarMenus();

                                    // Show the clicked menu
                                    sidebarMenu.style.display = 'block';
                                    currentOpenMenu = sidebarMenu; // Update the current open menu
                                }
                                
                            });

                            subtopicsContainer.appendChild(subtopicATag); 
                            
                        });
                        subtopicsContainer.style.display = 'block';

                        // toggle the caret icons
                        downIcon.style.display = 'none';
                        upIcon.style.display = 'block';
                        
                    }else{
                        alert('This topic has no subtopics yet.');
                    }
                })
                .catch(error => console.error('Error loading the form:', error));
            }
        })

    })
}

function addQuestion(topicId, subtopic_id){
    /*
        This function will load the AddQuestionAndChoices form dynamically.
        The topic and subtopic will be preloaded.
    */

    const route = `/management/portal/add_question_and_choices_dynamically`;

    fetch(route)
    .then(response => response.json())
    .then(data => {
        if (data.success){
            // Insert the form HTML into the management container
            const managementContainer = document.getElementById('management-container');
            managementContainer.innerHTML = data.add_question_and_choices_form_html;

            // populate the topic and subtopic form fields
            document.getElementById('topic-for-question').value = topicId;
            subtopicMenu = document.getElementById('subtopic-for-question');
            getSubtopics(topicId, subtopicMenu, function(){
                // subtopic menu won't be initialized until the menu has finished loading
                subtopicMenu.value = subtopic_id;
            });
            
            selectQuestionType(true);          

        }else{
            console.error('Failed to load the form.');
        }

    })
    .catch(error => console.error('Error loading the form:', error));
}

function getQuestionToEditFromSidebar(topicId, subtopicId, messages=[]){
    /*
        This function will load the EditQuestion form dynamically.
        The topic subtopic, and questions will be preloaded.
    */

    const route = `/management/portal/get_question_to_edit_dynamically`;
    fetch(route)
    .then(response => response.json())
    .then(data => {
        if (data.success){
            // Insert the form HTML into the management container
            const managementContainer = document.getElementById('management-container');
            managementContainer.innerHTML = data.edit_question_form_html;
            
            // populate the topic and subtopic form fields
            document.getElementById('topic-for-edit-question').value = topicId;
            subtopicMenu = document.getElementById('subtopic-for-edit-question');
            getSubtopics(topicId, subtopicMenu, function(){
                // subtopic menu won't be initialized until the menu has finished loading
                subtopicMenu.value = subtopicId;
                
            });

            loadQuestionsToEdit(subtopicId);
            
        }else{
            console.error('Failed to load the form.');
        }

    })
    .catch(error => console.error('Error loading the form:', error));
}

function getAllQuestionsToEditFromSidebar(topicId, subtopicId){

}

function addTopic(){
    const route = `/management/portal/add_topic`;

    // Create FormData object 
    const addTopicForm = document.getElementById('add-topic-form');
    const formData = new FormData(addTopicForm);

    // Retrieve the django CSRF token from the form
    //var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrftoken = formData.get('csrfmiddlewaretoken');
    
    fetch(route, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData,        
    })    
    .then(response => response.json())
    .then(data => {       
        document.getElementById('new-topic').focus();       
        if (data.success){ 
            addTopicForm.reset();             
            // update the sidebar with the new topic 
            const sidebar = document.querySelector('.sidebar');
            const aTag = document.createElement('a');
            aTag.setAttribute('href', '#');
            aTag.setAttribute('id', `topic-${data.topic_id}`);
            aTag.setAttribute('class', 'topic');
            aTag.setAttribute('data-topic-id', data.topic_id);
            aTag.textContent = data.topic_name;
            sidebar.appendChild(aTag);      
            
            // display success message
            let add_topic_msg = document.getElementById('add-topic-msg');
            add_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;

        } else {
            // errors
            let add_topic_msg = document.getElementById('add-topic-msg');
            add_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
                             
    })
    .catch(error => console.error('Error loading the add topic form:', error));   

}

function renameTopic(){
    const route = `/management/portal/rename_topic`;

    // Create FormData object 
    const renameTopicForm = document.getElementById('rename-topic-form');
    const formData = new FormData(renameTopicForm);

    // Retrieve the django CSRF token from the form
    const csrftoken = formData.get('csrfmiddlewaretoken');

    fetch(route, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData,
    })   
    .then(response => response.json())
    .then(data =>{
        document.getElementById('new-topic-name').focus();       
        clearMessages();

        if (data.success){  
            renameTopicForm.reset();
            // update the topic select menu to reflect the name change
            updateTopicSelectMenu('rename-topic'); 
            
            // update the sidebar with the new topic name
            let downIcon = document.getElementById(`caretdown-${data.topic_id}`);
            let upIcon = document.getElementById(`caretup-${data.topic_id}`);
            const aTag = document.getElementById(`topic-${data.topic_id}`);

            // Clear the existing content of the aTag without removing the caret
            aTag.innerHTML = ''; 
            aTag.append(data.renamed_topic);

            // Append both carets and preserve their visibility states
            if (downIcon) {
                aTag.appendChild(downIcon); 
                downIcon.style.display = downIcon.style.display; // Preserve current state
            } 

            if (upIcon) {
                aTag.appendChild(upIcon); 
                upIcon.style.display = upIcon.style.display; // Preserve current state
            } 
            
            // display success message
            let rename_topic_msg = document.getElementById('rename-topic-msg');
            rename_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            
        } else {
            // errors
            let rename_topic_msg = document.getElementById('rename-topic-msg');
            rename_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
        
    })
    .catch(error => console.error('Error loading the rename topic form:', error)); 
}

function updateTopicSelectMenu(formTopicId){
    const route = `/management/portal/get_topics`;
    fetch(route)
    .then(response => response.json())
    .then(data =>{
        
        if (data.success){
            
            const selectTopics = document.getElementById(formTopicId);
            // clear the existing subtopic options
            selectTopics.innerHTML = '';  
            
            // load the new topics menu, including the placeholder option
            // Add placeholder option
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = '--------';
            placeholderOption.selected = true;
            selectTopics.appendChild(placeholderOption);
            
            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                selectTopics.appendChild(option);
            }); 
             
        }else{
            // error occurred while retrieving topics
            let rename_topic_msg = document.getElementById('rename-topic-msg');
            rename_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
    })

}

function setupDeleteTopicModal(){   
    const selectTopicToDelete = document.getElementById('topic-to-delete');
    const deleteTopicButton = document.getElementById('delete-topic-btn');
    const modalElement = document.getElementById('confirm-delete-topic-modal');
    
    if (!modalElement || !deleteTopicButton || !selectTopicToDelete) {
        displayMessage('Unable to load the delete topic modal.', 'danger');
        return null;  // Exit early if essential elements are missing
    }

    if (selectTopicToDelete.options.length <= 1){
        displayMessage('There are no topics to delete.', 'info');  
            return null;  // No further setup needed if there are no valid topics
    }

    if (!selectTopicToDelete.value){
        // Display an error message if no topic is selected
        displayMessage('Please select a valid topic to delete.', 'danger');                        
        return null;  
    }
       
    // instantiate the confirmation modal
    const confirmDeleteTopicModal = new bootstrap.Modal(document.getElementById('confirm-delete-topic-modal'), {});
       
    clearMessages();
    confirmDeleteTopicModal.show(); 
    return confirmDeleteTopicModal;
                                   
}

function confirmTopicDeletion(confirmDeleteTopicModal){
    const selectTopicToDelete = document.getElementById('topic-to-delete');
    const selectedTopicId = selectTopicToDelete.value;
    deleteTopic(selectedTopicId, confirmDeleteTopicModal);
}

function deleteTopic(selectedTopicId, confirmDeleteTopicModal){    
    const deleteTopicForm = document.getElementById('delete-topic-form');
       
    const route = `/management/portal/delete_topic/${selectedTopicId}`;
    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
    fetch(route, {
        method: 'POST',
        headers: {
            //'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => response.json())
    .then(data => {        
        if (data.success){
            deleteTopicForm.reset(); // reset the form
            // update the topic select menu to reflect the topic deletion
            updateTopicSelectMenu('topic-to-delete'); 

            // Remove the deleted topic from the sidebar
            const topicElement = document.getElementById(`topic-${selectedTopicId}`);
            const subtopicsContainer = document.getElementById(`subtopicscontainer-${selectedTopicId}`);

            if (topicElement) {
                topicElement.remove();  
            }
            
            if (subtopicsContainer) {
                subtopicsContainer.remove();  
            }

            clearMessages();
                            
            // display success message
            let delete_topic_msg = document.getElementById('delete-topic-msg');
            delete_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            
        }else{
            clearMessages();
            // errors
            let delete_topic_msg = document.getElementById('delete-topic-msg');
            delete_topic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }

        // Close the modal
        confirmDeleteTopicModal.hide();
        
    })
    .catch(error => console.error('Topic deletion failed:', error));       
    //});
}
        
function addSubtopic(){
    const route = `/management/portal/add_subtopic`;

    // Retrieve the django CSRF token from the form
     const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
        topic_id : document.getElementById('topic-name-subtopic').value,
        name : document.getElementById('new-subtopic').value,                
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('new-subtopic').focus();
        if (data.success){
            // reset the add subtopic form
            document.getElementById('add-subtopic-form').reset();

            // update the sidebar with the new subtopic
            const topicId = data.topic_id;
            const subtopicsContainer = document.getElementById('subtopicscontainer-' + topicId);
            const topicATag = document.getElementById('topic-' + topicId);
            let upIcon = document.getElementById('caretup-' + topicId);
            let downIcon = document.getElementById('caretdown-' + topicId);  

            // downIcon won't exist if there are no subtopics yet for the chosen topic
            if (!downIcon){
                downIcon = document.createElement('i');
                downIcon.classList.add('fa', 'fa-caret-down');
                downIcon.setAttribute('id', `caretdown-${topicId}`);
                downIcon.style.display = 'none';
            }      

            // if this is the first subtopic for the topic, enable the subtopics container and up caret
            if (subtopicsContainer.children.length == 0){
                subtopicsContainer.innerHTML = '';
                // enable the subtopics container and display the up caret
                subtopicsContainer.style.display = 'block'; 
                upIcon.style.display = 'block'; 
                downIcon.style.display = 'none';                
            }

            const subtopicATag = document.createElement('a');
            subtopicATag.setAttribute('href', '#');
            subtopicATag.setAttribute('id', `subtopic-${data.subtopic_id}`);
            subtopicATag.setAttribute('class', 'subtopic');
            subtopicATag.setAttribute('data-subtopic-id', data.subtopic_id);
            subtopicATag.textContent = data.subtopic_name;
            subtopicsContainer.appendChild(subtopicATag); 

            // create a span for the question icon and badge.
            // This will display the number of questions for each subtopic
            const iconSpan = document.createElement('span');
            iconSpan.setAttribute('class', 'icon-with-badge');

            // create the question mark icon
            const questionIcon = document.createElement('i');
            questionIcon.setAttribute('class', 'fas fa-question-circle');

            // Create the badge element to display the number of questions
            const badge = document.createElement('span');
            badge.setAttribute('class', 'badge');
            badge.setAttribute('id', `badge-${data.subtopic_id}`);
            badge.textContent = 0;

            // Append the question icon and badge to the icon span
            iconSpan.appendChild(questionIcon);
            iconSpan.appendChild(badge);

            // Append the icon span to the subtopic link
            subtopicATag.appendChild(iconSpan);

            // display success message
            clearMessages();
            let add_subtopic_msg = document.getElementById('add-subtopic-msg');
            add_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;

        } else {
            // errors
            clearMessages();
            document.getElementById('new-subtopic').value = ''; // clear out the subtopic name field
            document.getElementById('new-subtopic').focus();
            let add_subtopic_msg = document.getElementById('add-subtopic-msg');
            add_subtopic_msg.innerHTML = ''; // clear out any old messages
            add_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;

        }
                             
    })
    .catch(error => console.error('Error loading the form:', error));
}

function renameSubtopic(){
    const route = `/management/portal/rename_subtopic`;

    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            topic_id : document.getElementById('topic-for-renamed-subtopic').value,
            subtopic_id : document.getElementById('choose-subtopic-to-rename').value,
            new_subtopic_name : document.getElementById('new-subtopic-name').value               
        })
    })   
    .then(response => response.json())
    .then(data =>{
        document.getElementById('new-subtopic-name').focus();       
        clearMessages();
        
        if (data.success){  
            document.getElementById('rename-subtopic-form').reset(); // reset the form
            
            // update the sidebar with the new subtopic name
            const subtopicATag = document.getElementById(`subtopic-${data.subtopic_id}`);
            
            if (subtopicATag){
                // get the iconSpan associated with the subtopcicATag
                const iconSpan = subtopicATag.querySelector('.icon-with-badge');

                subtopicATag.textContent = data.new_subtopic_name;

                if (iconSpan){
                    subtopicATag.appendChild(iconSpan);
                }
            }        

            // display success message
            let rename_subtopic_msg = document.getElementById('rename-subtopic-msg');
            rename_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            
        } else {
            // errors
            let rename_subtopic_msg = document.getElementById('rename-subtopic-msg');
            rename_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
        
    })
    .catch(error => console.error('Error loading the form:', error));    
}


function setupSelectSubtopicToRename(){
    // topic dropdown menu
    const selectTopicForRenamedSubtopic = document.getElementById('topic-for-renamed-subtopic');

    // subtopic dropdown menu
    const selectSubtopicToRename = document.getElementById('choose-subtopic-to-rename');
    
    if (selectTopicForRenamedSubtopic){
        // must be at least one valid topic
        const validTopicOptions = selectTopicForRenamedSubtopic.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics or subtopics to rename.', 'info');
            return;
        }
        
        const selectedTopicId = selectTopicForRenamedSubtopic.value;
        if (!selectedTopicId){
            displayMessage('There are no topics/subtopics to rename.', 'info');
            return;
        } else{            
            getSubtopicsToRename(selectedTopicId, selectSubtopicToRename);
        }                   

    }
}

function getSubtopicsToRename(selectedTopicId, selectSubtopicToRename){
    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics/${selectedTopicId}`;

    fetch(route)
    .then(response => response.json())
    .then(data =>{
        
        if (data.success){
            // clear the existing subtopic options
            selectSubtopicToRename.innerHTML = '';

            const placeholderOption = placeholderDefaultOption();
            selectSubtopicToRename.appendChild(placeholderOption);
            
            data.subtopics.forEach(subtopic => {
            const option = document.createElement('option');
            option.value = subtopic.id;
            option.textContent = subtopic.name;
            selectSubtopicToRename.appendChild(option);
            }); 
            
            const validSubtopicOptions = selectSubtopicToRename.options.length > 1;

            if (!validSubtopicOptions){
                let rename_subtopic_msg = document.getElementById('rename-subtopic-msg');
                if (rename_subtopic_msg){
                    rename_subtopic_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }
        }else{
            let rename_subtopic_msg = document.getElementById('rename-subtopic-msg');
            if (rename_subtopic_msg){
                rename_subtopic_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There are no available subtopics for the chosen topic', 'info');
            return;    
        } 
    })
}

//function setupDeleteSubtopicModal(){
//    setupSelectSubtopicToDelete();
//    setupSubtopicToDeleteButton(); 
//}

function setupSelectSubtopicToDelete(){
    const deleteSubtopicButton = document.getElementById('delete-subtopic-btn');
    const selectTopic = document.getElementById('topic-to-choose');
    const selectSubtopic = document.getElementById('subtopic-to-choose');   

    if (selectTopic){
        // must be at least one valid topic
        const validOptions = selectTopic.options.length > 1;

        if (!validOptions){
            displayMessage('There are no topics or subtopics to delete.', 'info');
            return;
        }
        
        const selectedTopicId = selectTopic.value;
        if (!selectedTopicId){
            displayMessage('No topic was selected.', 'info');
            return;
        } else{            
            deleteSubtopicButton.setAttribute('data-topic-id', selectedTopicId);
            getSubtopicsToDelete(selectedTopicId, deleteSubtopicButton);
        }
              
    }
}

function getSubtopicsToDelete(selectedTopicId, deleteSubtopicButton){
    const selectSubtopic = document.getElementById('subtopic-to-choose');

    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics/${selectedTopicId}`;
   
    fetch(route)
    .then(response => response.json())
    .then(data => {
        if (data.success){
            // clear the existing subtopic options
            selectSubtopic.innerHTML = '';

            // load the subtopics, including the placeholder option
            const placeholderOption = placeholderDefaultOption();
            selectSubtopic.appendChild(placeholderOption);

            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                selectSubtopic.appendChild(option);
            });  
        
            if (selectSubtopic){
                const validSubtopicOptions = selectSubtopic.options.length > 1;
                if (!validSubtopicOptions){
                    displayMessage('There are no available subtopics for the chosen topic', 'info');
                    return;
                }
                                           
            }
            
        }else{
            displayMessage('There was a problem retrieving subtopics for this topic', 'info');
            return;    
        }      

    })
}

function setupDeleteSubtopicModal(){
    const deleteSubtopicButton = document.getElementById('delete-subtopic-btn');
    const selectSubtopic = document.getElementById('subtopic-to-choose');
    const modalElement = document.getElementById('confirm-delete-subtopic-modal');  
        
    // Check if the delete button, modalElement, or subtopic menu exists before setting properties
    if (!deleteSubtopicButton || !modalElement || !selectSubtopic) {
        return null;  // Early exit to avoid further errors
    }

    const topicId = deleteSubtopicButton.dataset.topicId;
    const selectedSubtopicId = selectSubtopic.value;
    
    if (!selectedSubtopicId){
        displayMessage('No subtopic was selected', 'info');
        return;
    } else {
        deleteSubtopicButton.setAttribute('data-subtopic-id', selectedSubtopicId);                                             
    }  
    const subtopicId = deleteSubtopicButton.getAttribute('data-subtopic-id');
                
    if (!topicId){
        // Display an error message if no topic is selected
        clearMessages();
        displayMessage('Please select a topic.', 'danger');                        
        return null;  
    }

    if (!subtopicId){
        clearMessages();
        // Display an error message if no topic is selected
        displayMessage('Please select a subtopic.', 'danger');                        
        return null;  
    }

    // instantiate the confirmation modal
    const confirmDeleteSubtopicModal = new bootstrap.Modal(document.getElementById('confirm-delete-subtopic-modal'), {});
            
    clearMessages();
    confirmDeleteSubtopicModal.show(); 
    return confirmDeleteSubtopicModal;                               
    
}

function confirmSubtopicDeletion(confirmDeleteSubtopicModal){
    const deleteSubtopicButton = document.getElementById('delete-subtopic-btn');
    deleteSubtopic(deleteSubtopicButton, confirmDeleteSubtopicModal);
}

function deleteSubtopic(deleteSubtopicButton, confirmDeleteSubtopicModal){
    const confirmDeleteSubtopicButton = document.getElementById('confirm-delete-subtopic-button');
    if (confirmDeleteSubtopicButton){
        
        const topicId = deleteSubtopicButton.getAttribute('data-topic-id');
        const subtopicId = deleteSubtopicButton.getAttribute('data-subtopic-id');

        // get the remaining number of subtopics for the sidebar
        const route1 = `/management/portal/get_subtopics/${topicId}`;
        fetch(route1)
        .then(response => response.json())
        .then(subtopicsData => {
            if (subtopicsData.success){                   
                let remainingSubtopics = subtopicsData.subtopics_count;

                // delete the subtopic
                const route = `/management/portal/delete_subtopic/${subtopicId}`;
                // Retrieve the django CSRF token from the form
                let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(route, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    
                })
                .then(response => response.json())
                .then(data => {                
                    if (data.success){
                        document.getElementById('delete-subtopic-form').reset(); // reset the form
    
                        // clear the delete button data attributes
                        deleteSubtopicButton.setAttribute('data-topic-id', '');
                        deleteSubtopicButton.setAttribute('data-subtopic-id', '');
    
                        // Remove the deleted subtopic from the sidebar                   
                        //const subtopicsContainer = document.getElementById(`subtopicscontainer-${topicId}`);
                        const subtopicElement = document.getElementById(`subtopic-${subtopicId}`);                                       
                        
                        if (subtopicElement){
                            subtopicElement.remove();
                                
                        }
                        remainingSubtopics = remainingSubtopics - 1;
                                                                            
                        // if the last subtopic was deleted, remove the up/down caret from the sidebar
                        if (remainingSubtopics == 0){
                            let upIcon = document.getElementById(`caretup-${topicId}`);
                            let downIcon = document.getElementById(`caretdown-${topicId}`);
                            
                            if (upIcon){
                                upIcon.style.display = 'none';
                            }
                            if (downIcon){
                                downIcon.style.display = 'none';
                            }
                        }
                            
                        clearMessages();                                   
                        // display success message
                        let delete_subtopic_msg = document.getElementById('delete-subtopic-msg');
                        delete_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
                        
                    }else{
                        clearMessages();
                        // errors
                        let delete_subtopic_msg = document.getElementById('delete-subtopic-msg');
                        delete_subtopic_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
                    }
        
                    // Close the modal
                    confirmDeleteSubtopicModal.hide();
                    
                })
                .catch(error => console.error('Subtopic deletion failed:', error));
            }
        })
        .catch(error => console.error('Failed to retrieve subtopics:', error));          
                      
        
    }
}

function addQuestionAndChoices(){
    const route = `/management/portal/add_question_and_choices`;

    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Retrieve the add choice forms (must be at least two)
    let choices = [];
    const choiceForms = document.querySelectorAll('.choice-form');
    
    choiceForms.forEach((choiceForm, index) => {
        let choiceTextInput = choiceForm.querySelector(`[name="${index}-text"]`);
        let isCorrectInput = choiceForm.querySelector(`[name="${index}-is_correct"]`);

        // check for disabled forms
        if (!choiceTextInput.disabled && !isCorrectInput.disabled){
            let choiceText = choiceTextInput.value;
            let isCorrect = isCorrectInput.checked;
            choices.push({
                'text': choiceText,
                'is_correct': isCorrect
            });
        }
    });

    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            // question form values
            topic_id : document.getElementById('topic-for-question').value,
            subtopic_id : document.getElementById('subtopic-for-question').value,
            question_text : document.getElementById('new-question').value,  
            question_type : document.getElementById('question-type').value,
            // choice forms
            choices : choices
        })
    })   
    .then(response => response.json())
    .then(data => {
                
        if (data.success){  
            // repopulate the topic, subtopic, and question type fields
            // since it's likely that a user will add multiple questions for the same topic/subtopic combo
            document.getElementById('topic-for-question').value = data.topic_id;
            document.getElementById('subtopic-for-question').value = data.subtopic_id;
            document.getElementById('question-type').value = data.question_type_id;

            // update the sidebar question count
            let badge = document.getElementById('badge-' + data.subtopic_id);
            if (badge){
                // Get the current value of the badge and convert it to an integer
                let badgeValue = parseInt(badge.textContent, 10);

                // Update the question count
                badgeValue += 1;
        
                // Update the badge text content with the new question count
                badge.textContent = badgeValue;
                   
            }         

            // clear out the question field and choice forms
            document.getElementById('new-question').value = '';
            const addChoicesContainer = document.getElementById('add-choices-container');
            addChoicesContainer.innerHTML = '';

            // clear out any error messages on form fields
            document.getElementById('new-question').classList.remove('is-error');
            document.getElementById('question-text-error').textContent = '';

            // clear out error messages in the answer-choice-instructions div
            document.getElementById('answer-choice-instructions').textContent = '';
            
            // load blank choice forms
            data.add_choice_forms.forEach(addChoiceForm =>{
                const addChoiceDiv = document.createElement('div');
                addChoiceDiv.innerHTML = addChoiceForm;
                addChoicesContainer.appendChild(addChoiceDiv);
            });
            selectQuestionType(onLoad=true);

            // display success message
            let add_question_and_choices_msg = document.getElementById('add-question-and-choices-msg');
            add_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
                        
        } else {
            // question field errors
            const questionField = document.getElementById('new-question');
            const questionError = document.getElementById('question-text-error');
            questionField.classList.remove('is-error');
            questionError.textContent = '';

            if (data.question_errors && data.question_errors.question_text){
                questionField.classList.add('is-error');
                questionError.textContent = data.question_errors.question_text;
            }

            // answer choice errors
            const instructionsDiv = document.getElementById('answer-choice-instructions');
            instructionsDiv.innerHTML = '';
           
            if (data.choice_errors && data.choice_errors.choices){            
                const errorMessage = document.createElement('div');
                errorMessage.classList.add('text-danger') // bootstrap class
                errorMessage.textContent = data.choice_errors.choices;
                instructionsDiv.appendChild(errorMessage);                
            }

            if (data.messages && data.messages.length > 0){
                let add_question_and_choices_msg = document.getElementById('add-question-and-choices-msg');
                add_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            }
        }
    })

}

function setupSelectSubtopicsForQuestion(){
    const topicMenu = document.getElementById('topic-for-question');
    const subtopicMenu = document.getElementById('subtopic-for-question');
    
    if (topicMenu){
        // must be at least one valid topic
        const validTopicOptions = topicMenu.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics available.', 'info');
            return;
        }

        // add event listeneer for the topic dropdown menu
        //topicMenu.addEventListener('change', function(){
            const selectedTopicId = topicMenu.value;
           
            if (!selectedTopicId){
                displayMessage('There are no topics available.', 'info');
                return;
            } else{  
                         
                getSubtopics(selectedTopicId, subtopicMenu);
            }

        //})
        
    }
}

function selectQuestionType(onLoad=false){
    const questionType = document.getElementById('question-type');
    const addChoiceButton = document.getElementById('add-choice-btn');
    const instructions = document.getElementById('answer-choice-instructions');
    
    if (questionType){         
        const selectedQuestionType = questionType.value;
        
        const route = `/management/portal/get_question_type_name/${selectedQuestionType}`; 
            
        // get the question type name from the QuestionType table
        fetch(route)
        .then(response => response.json())
        .then(data => {
            if (data.success){
                const questionTypeName = data.name;
                
                if (questionTypeName === 'True/False'){
                    // only 2 choices allowed in the form
                    // prepopulate the choices with True and False
                    // Set the text fields to "True" and "False" and make them read-only
                    document.getElementById('id_0-text').value = "True";
                    document.getElementById('id_0-text').readOnly = true;
                    document.getElementById('id_1-text').value = "False";
                    document.getElementById('id_1-text').readOnly = true;
                                      
                    // hide any other choice forms
                    for (i=2; i<=5; i++){
                        if (document.getElementById(`id_${i}-text`)) {
                            document.getElementById(`id_${i}-text`).value = "";
                            document.getElementById(`id_${i}-text`).disabled = true;
                            document.getElementById(`id_${i}-is_correct`).disabled = true;
                        }
                    }
                    
                    // Hide the add choice button
                    addChoiceButton.style.display = 'none';

                }else{
                    for (let i = 0; i <= 5; i++) {
                        if (document.getElementById(`id_${i}-text`)) {
                            document.getElementById(`id_${i}-text`).value = "";
                            document.getElementById(`id_${i}-text`).readOnly = false;
                            document.getElementById(`id_${i}-text`).disabled = false;
                            document.getElementById(`id_${i}-is_correct`).disabled = false;
                            document.getElementById(`id_${i}-is_correct`).checked = false;
                        }
                    }

                    // enable the add choice button for the other question types
                    addChoiceButton.style.display = 'block';
                }
                // load the instructions for answering the question
                if (questionTypeName === 'True/False' || questionTypeName === 'Multiple Choice'){
                    instructions.textContent = 'Choose one correct answer only.';
                }
                else if (questionTypeName === 'Multiple Answer'){
                    instructions.textContent = 'Choose two or more correct answers.';    
                }
                // on form load, ensure the message is displayed immediately
                if (onLoad) {
                    instructions.style.display = 'block';
                }

            }else{
                // errors
                let add_question_and_choices_msg = document.getElementById('add-question-and-choices-msg');
                add_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            }
        
        })
        .catch(error => console.error('Error retrieving questiontype name:', error));            
        
    }
}

function questionTypeInstructions(questionTypeName){
    const instructions = document.getElementById('question-type-instructions');
    if (questionTypeName === 'True/False' || questionTypeName === 'Multiple Choice'){
        instructions.textContent = 'Choose one correct answer only.';
    }
    else if (questionTypeName === ' Multiple Answer'){
        instructions.textContent = 'Choose two or more correct answers.';    
    }
}

function addAnotherChoice(){   
    addChoicesContainer = document.getElementById('add-choices-container');    
    const addChoiceButton = document.getElementById('add-choice-btn');

    if (addChoiceButton){   
            
        // clone the choice form and get all the fields and labels           
        const newChoiceForm = addChoicesContainer.firstElementChild.cloneNode(true);
                    
        let choiceFields = newChoiceForm.querySelectorAll('textarea, input');
        let choiceLabels = newChoiceForm.querySelectorAll('label');
        
        let choiceCount = addChoicesContainer.childElementCount;       
                        
        // clear the values from the cloned choice form
        choiceFields.forEach(function(field){
            field.value = '';
            if (field.type === 'checkbox'){
                field.checked = false;
            }
        });
        
        choiceCount++;
        
        // create the id for the new choice form
        newChoiceForm.id = 'add-choice-' + choiceCount;
        
        // update the form prefix
        const newPrefix = (choiceCount-1).toString();
            
        choiceFields.forEach(function(field){
            //if (field.name){
            //    field.name = field.name.replace(/\d+/, newPrefix);
            //}
            //if (field.id){
            //    field.id = field.id.replace(/\d+/, newPrefix);
            //} 
            if (field.name.includes('choice-id')) {
                // Assign a unique index for the new choice-id field
                field.name = `choice-id-${choiceCount}`;
                field.id = `choice-id-${choiceCount}`;
                field.value = ''; // Ensure the new choice-id is blank
            } else {
                // Update the name and ID for other fields
                if (field.name) {
                    field.name = field.name.replace(/\d+/, newPrefix);
                }
                if (field.id) {
                    field.id = field.id.replace(/\d+/, newPrefix);
                }
            }           
        });

        // Update the for attribute of labels
        choiceLabels.forEach(function(label) {
            if (label.htmlFor) {
                label.htmlFor = label.htmlFor.replace(/\d+/, newPrefix);
            }
            
        });
          
        addChoicesContainer.appendChild(newChoiceForm); 
           
    }   
}

function addChoiceToEditForm(){
    editChoicesContainer = document.getElementById('edit-choices-container');    
    const addChoiceButtonEdit = document.getElementById('add-choice-btn-edit');
    
    if (addChoiceButtonEdit){

        if (editChoicesContainer){
            // clone the choice form and get all the fields and labels           
            const newChoiceForm = editChoicesContainer.firstElementChild.cloneNode(true);                      
            let choiceFields = newChoiceForm.querySelectorAll('input, textarea');
            let choiceLabels = newChoiceForm.querySelectorAll('label');           
            let choiceCount = editChoicesContainer.childElementCount; 

            // clear the values from the cloned choice form
            choiceFields.forEach(function(field){
                field.value = '';
                if (field.type === 'checkbox'){
                    field.checked = false;
                }
            });

            // create the id for the new choice form
            choiceCount++;
            newChoiceForm.id = 'edit-choice-' + choiceCount;

            // update the form prefix
            const newPrefix = (choiceCount-1).toString();

            choiceFields.forEach(function(field){
                
                if (field.name.includes('choice-id')) {
                    // Assign a unique index for the new choice-id field
                    field.name = `choice-id-${choiceCount}`;
                    field.id = `choice-id-${choiceCount}`;
                    field.value = ''; // Ensure the new choice-id is blank
                } else {
                    // Update the name and ID for other fields
                    if (field.name) {
                        field.name = field.name.replace(/\d+/, newPrefix);
                    }
                    if (field.id) {
                        field.id = field.id.replace(/\d+/, newPrefix);
                    }
                }
                       
            });

            // Update the for attribute of labels
            choiceLabels.forEach(function(label) {
                if (label.htmlFor) {
                    label.htmlFor = label.htmlFor.replace(/\d+/, newPrefix);
                }               
            });
            
            editChoicesContainer.appendChild(newChoiceForm);
            
        }else{
            console.error('edit choice container not found.');
        }
    }

}

function selectTopicForQuestionToEdit(){
    const topicMenu = document.getElementById('topic-for-edit-question');
    const subtopicMenu = document.getElementById('subtopic-for-edit-question');
    
    if (topicMenu){
        // must be at least one valid topic
        const validTopicOptions = topicMenu.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics available.', 'info');
            return;
        }
        
        const selectedTopicId = topicMenu.value;
        
        if (!selectedTopicId){
            displayMessage('There are no topics available.', 'info');
            return;
        } else{                         
            getSubtopicsForQuestionToEdit(selectedTopicId, subtopicMenu);
        }   
    }
}

function getSubtopicsForQuestionToEdit(selectedTopicId, subtopicMenu){
    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics_with_questions/${selectedTopicId}`;
    fetch(route)
    .then(response => response.json())
    .then(data =>{
        
        if (data.success){
            // clear the existing subtopic options
            subtopicMenu.innerHTML = '';
           
            // load the new subtopics, including the placeholder option
            const placeholderOption = placeholderDefaultOption();
            subtopicMenu.appendChild(placeholderOption);
            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                subtopicMenu.appendChild(option);
            }); 
            
            const validSubtopicOptions = subtopicMenu.options.length > 1;

            if (!validSubtopicOptions){
                let edit_question_msg = document.getElementById('edit-question-msg');
                if (edit_question_msg){
                    edit_question_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }
                
        }else{
            let edit_question_msg = document.getElementById('edit-question-msg');
            if (edit_question_msg){
                edit_question_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There are no available subtopics for the chosen topic', 'info');
            return;    
        } 
    })
}

function loadQuestionsToEdit(selectedSubtopicId){
    const questionMenu = document.getElementById('question-to-edit');
    
    // get all the questions for the chosen subtopic
    const route = `/management/portal/load_questions/${selectedSubtopicId}`;

    fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            // clear the existing question menu options
            questionMenu.innerHTML = '';

            // load the new questions, including the placeholder option
            const placeholderOption = placeholderDefaultOption();
            questionMenu.appendChild(placeholderOption);

            data.questions.forEach(question => {
                const option = document.createElement('option');
                option.value = question.id;
                option.textContent = question.text;
                questionMenu.appendChild(option);
            }); 
            
            const validQuestionOptions = questionMenu.options.length > 1;

            if (!validQuestionOptions){
                let edit_question_msg = document.getElementById('edit-question-msg');
                if (edit_question_msg){
                    edit_question_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available questions for the chosen subtopic', 'info');
                return;
            }

        }else{
            let edit_question_msg = document.getElementById('edit-question-msg');
            if (edit_question_msg){
                edit_question_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There are no available questions for the chosen subtopic', 'info');
            return;    
        } 

    })
}

function editQuestionAndChoices(){
    const route = `/management/portal/edit_question_and_choices`;

    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Retrieve the add choice forms (must be at least two)
    let choices = [];
    const choiceForms = document.querySelectorAll('.choice-form');

    choiceForms.forEach((choiceForm, index) => {
        let choiceIdInput = choiceForm.querySelector(`[name="choice-id-${index + 1}"]`);
        let choiceTextInput = choiceForm.querySelector(`[name="${index}-text"]`);
        let isCorrectInput = choiceForm.querySelector(`[name="${index}-is_correct"]`);

        let choiceId = '';
        if (choiceIdInput){
            choiceId = choiceIdInput.value;
        }
         
              
        let choiceText = choiceTextInput.value;
        let isCorrect = isCorrectInput.checked;
        choices.push({
            'id': choiceId,
            'text': choiceText,
            'is_correct': isCorrect
        });       
    });

    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            // question form values
            question_id : document.getElementById('question-id').value,
            question_text : document.getElementById('question-text').value,  
            subtopic_id : document.getElementById('subtopic-id').value,
            question_name : document.getElementById('question-name').value,
            question_type_id : document.getElementById('question-type-id').value,
            // choice forms
            choices : choices
        })
    })   
    .then(response => response.json())
    .then(data => {
        clearMessages();
        let messageContainer = document.querySelector('.error-msg');
        
        if (data.success){ 
            document.getElementById('edit-choices-container').innerHTML = '';              
            getQuestionToEditDynamically(data.messages);                                  
        }else{

            // question field errors
            const questionField = document.getElementById('question-text');
            const questionError = document.getElementById('question-text-error');
            questionField.classList.remove('is-error');
            questionError.textContent = '';

            if (data.question_errors && data.question_errors.question_text){
                questionField.classList.add('is-error');
                questionError.textContent = data.question_errors.question_text;
            }

            // answer choice errors
            const answerChoiceErrors = document.getElementById('answer-choice-errors');
            answerChoiceErrors.innerHTML = '';

            if (data.choice_errors && data.choice_errors.choices){
                const errorMessage = document.createElement('div');
                errorMessage.classList.add('text-danger');
                errorMessage.textContent = data.choice_errors.choices;
                answerChoiceErrors.appendChild(errorMessage);
            }

            if (data.messages && data.messages.length > 0){
                let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
                edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            }
            
        }
    })
    .catch(error => console.error('Error submitting the form', error));

}

function getQuestionToEditDynamically(messages=[]){
    const route = `/management/portal/get_question_to_edit_dynamically`;
    
    fetch(route)
    .then(response => response.json())
    .then(data => {
        
        if (data.success){
            const managementContainer = document.getElementById('management-container');
            managementContainer.innerHTML = '';
            managementContainer.innerHTML = data.edit_question_form_html;
            
            let messageContainer = document.querySelector('.error-msg');
            if (messages){
                messages.forEach(message =>{
                    let msgDiv = document.createElement('div');
                    msgDiv.className = `alert alert-${message.tags}`;
                    msgDiv.role = 'alert';
                    msgDiv.textContent = message.message;
                    messageContainer.appendChild(msgDiv);
                });
            }            
        }
    })
    .catch(error => console.error('Error loading the form', error));
    
}

function selectTopicForAllQuestionsToEdit(){
    const topicMenu = document.getElementById('topic-for-get-all-questions');
    const subtopicMenu = document.getElementById('subtopic-for-get-all-questions');
    
    if (topicMenu){
        // must be at least one valid topic
        const validTopicOptions = topicMenu.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics available.', 'info');
            return;
        }

        
        const selectedTopicId = topicMenu.value;
        
        if (!selectedTopicId){
            displayMessage('There are no topics available.', 'info');
            return;
        } else{                          
            getSubtopicsForAllQuestionsToEdit(selectedTopicId, subtopicMenu);
        }        
    }   
}

function getSubtopicsForAllQuestionsToEdit(selectedTopicId, subtopicMenu){
// get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics_with_questions/${selectedTopicId}`;
    
    fetch(route)
    .then(response => response.json())
    .then(data =>{        
        if (data.success){
            // clear the existing subtopic options
            subtopicMenu.innerHTML = '',
           
            // load the new subtopics, including the placeholder option
            //subtopicMenu.innerHTML = '<option value="" selected ="">--------</option>';
            placeholderOption = placeholderDefaultOption();
            subtopicMenu.appendChild(placeholderOption);
            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                subtopicMenu.appendChild(option);
            }); 
            
            const validSubtopicOptions = subtopicMenu.options.length > 1;

            if (!validSubtopicOptions){
                let edit_all_questions_msg = document.getElementById('get-all-questions-msg');
                if (edit_all_questions_msg){
                    edit_all_questions_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }
                
        }else{
            let edit_all_questions_msg = document.getElementById('get-all-questions-msg');
            if (edit_all_questions_msg){
                edit_all_questions_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There are no available subtopics for the chosen topic', 'info');
            return;    
        } 
    })
}

function selectQuestionToEdit(){
    // retrieve the EditQuestionForm values
    topicId = document.getElementById('topic-for-edit-question').value;
    subtopicId = document.getElementById('subtopic-for-edit-question').value;
    questionId = document.getElementById('question-to-edit').value;

    // use promises so that the asynchronous operations all complete before executing code that
    // depends upon their results
  
    // retrieve the topic name from the topic id
    const route1 = `/management/portal/get_topic_name/${topicId}`;
    const topicNamePromise = fetch(route1)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            return data.topic_name;
        }else{
        // errors
        let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
        edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        return '';  
        }     
    })
    .catch(error => {
        console.error('Error fetching topic name:', error);
        return '';
    });

    // retrieve the subtopic name from the subtopic id
    const route2 = `/management/portal/get_subtopic_name/${subtopicId}`;
    const subtopicNamePromise = fetch(route2)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            return data.subtopic_name;
            
        }else{
            // errors
            let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
            edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            return '';
        }      
    })
    .catch(error => {
        console.error('Error fetching subtopic name:', error);
        return '';
    });

    // retrieve the question data
    const route = `/management/portal/load_question_to_edit/${questionId}`;
    
    const questionDataPromise = fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            return data;        
        }else{
            // errors
            let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
            edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            return null;
        }
    }) 
    .catch(error => {
        console.error('Error loading question data:', error);
        return null;
    });

    // resolve all the promises
    Promise.all([topicNamePromise, subtopicNamePromise, questionDataPromise])
    .then(([topicName, subtopicName, questionData]) => {
        if (questionData) {
            // Insert the form HTML into the management container
            const managementContainer = document.getElementById('management-container');
            managementContainer.innerHTML = questionData.edit_question_and_choices_form_html;

            // set form values
            document.getElementById('topic-name').value = topicName;
            document.getElementById('subtopic-name').value = subtopicName;
            document.getElementById('subtopic-id').value = subtopicId;
            document.getElementById('question-name').value = questionData.question.question_type.name;
            document.getElementById('question-text').value = questionData.question.text;
            document.getElementById('question-type-id').value = questionData.question.question_type.id;

            // iterate over the choice forms array and prepopulate the blank choice forms
            questionData.choices.forEach((choice, index) => {
                document.querySelector(`#edit-choice-${index + 1} textarea[name$="text"]`).value = choice.text;
                document.querySelector(`#edit-choice-${index + 1} input[name$="is_correct"]`).checked = choice.is_correct;
            });
            
            // Can't change the value of True and False
            if (questionData.question.question_type.name === 'True/False'){                
                document.getElementById('id_0-text').readOnly = true;
                document.getElementById('id_1-text').readOnly = true;

                // 'read-only' class will be used to gray out the choice text field 
                document.getElementById('id_0-text').classList.add('read-only');               
                document.getElementById('id_1-text').classList.add('read-only');
            }
            
        }
    })
    .catch(error => {
        console.error('Error processing form data:', error);
    });
}

function setupDeleteQuestionDialog(){
    
    const dialogElement = document.getElementById('confirm-delete-question-dialog');

    if (dialogElement){        
        dialogElement.showModal();
    }else {
        console.error('Dialog element with ID confirm-delete-question-dialog not found.');
        return; 
    }

}

function cancelQuestionDialog(){
    const dialogElement = document.getElementById('confirm-delete-question-dialog');
    dialogElement.close();
}

function setupDeleteQuestionModal(){
    const deleteQuestionButton = document.getElementById('delete-question-btn');
    const modalElement = document.getElementById('confirm-delete-question-modal'); 
            
    if (modalElement){
        // Check if the delete button exists before setting properties
        if (!deleteQuestionButton) {
            return;  // Early exit to avoid further errors
        }  

        const confirmDeleteQuestionModal = new bootstrap.Modal(document.getElementById('confirm-delete-question-modal'), {});
        
        deleteQuestionButton.addEventListener('click', function(e){        
            confirmDeleteQuestionModal.show();
            deleteQuestion(confirmDeleteQuestionModal); 
        })
                         
    }else {
        console.error('Modal element with ID confirm-delete-question-modal not found.');
        return; 
    }
    
}

function deleteQuestion(){  
    const dialogElement = document.getElementById('confirm-delete-question-dialog');          
    const questionId = document.getElementById('question-id').value;
    const subtopicId = document.getElementById('subtopic-id').value;
    const route = `/management/portal/delete_question/${questionId}`;        
       
    // Retrieve the django CSRF token from the form
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
    fetch(route, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            subtopic_id : subtopicId, 
                
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success){
            
            // update sidebar menu with new question count
            badge = document.getElementById(`badge-${subtopicId}`);
            if (badge){
                badge.textContent = data.question_count;
            }

            dialogElement.close();
            getQuestionToEditDynamically(data.messages);
            
        }else{
            // errors
            let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
            edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            
            // reload the form
            dialogElement.close();
            getQuestionToEditDynamically(data.messages);
        }
        
    })
    .catch(error => console.error('Question deletion failed:', error));  
    dialogElement.close();
}  

function deleteAllQuestions(){
    const deleteAllQuestionsButton = document.getElementById('delete-all-questions-btn');
    
    if (deleteAllQuestionsButton){
        const questionId = document.getElementById('question-id').value;
        const subtopicId = document.getElementById('subtopic-id').value;
        const pageNumber = document.getElementById('page').value;
        const route = `/management/portal/delete_question/${questionId}`;

        deleteAllQuestionsButton.addEventListener('click', function(e){
            e.preventDefault();
            
            const confirmDelete = confirm("Are you sure? This operation can't be undone.");
            if (!confirmDelete) return;

            // Retrieve the django CSRF token from the form
            var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
            fetch(route, {
                method: 'DELETE',
                headers: {

                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    question_id : questionId,
                    subtopic_id : document.getElementById('subtopic-id').value, 
                    page: pageNumber,  
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    updatePagination(data.new_page_number)
                }else{
                    // errors
                    let edit_question_and_choices_msg = document.getElementById('edit-question-and-choices-msg');
                    edit_question_and_choices_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
                }
            })
            .catch(error => console.error('Deletion failed:', error));
        })     

    }

}

function selectTopicForAddExplanation(){
    const topicMenu = document.getElementById('topic-for-add-explanation');
    const subtopicMenu = document.getElementById('subtopic-for-add-explanation');
    
    if (topicMenu){
        // must be at least one valid topic
        const validTopicOptions = topicMenu.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics available.', 'info');
            return;
        }

        const selectedTopicId = topicMenu.value;
        clearMessages();
        if (!selectedTopicId){
            displayMessage('There are no topics available.', 'info');
            return;
        } else{                          
            getSubtopicsForAddExplanationForm(selectedTopicId, subtopicMenu);
        }        
    }    
}

function getSubtopicsForAddExplanationForm(selectedTopicId, subtopicMenu){
    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics_with_questions_without_explanations/${selectedTopicId}`;
    fetch(route)
    .then(response => response.json())
    .then(data =>{
        
        if (data.success){
            // clear the existing subtopic options
            subtopicMenu.innerHTML = '',
        
            // load the new subtopics, including the placeholder option
            placeholderOption = placeholderDefaultOption();
            subtopicMenu.appendChild(placeholderOption);
            
            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                subtopicMenu.appendChild(option);
            }); 
            
            const validSubtopicOptions = subtopicMenu.options.length > 1;

            if (!validSubtopicOptions){
                let add_explanation_msg = document.getElementById('add-explanation-msg');
                if (add_explanation_msg){
                    add_explanation_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }else{
                // add event listener to subtopic menu
                //.addEventListener('change', function(){
                //    const selectedSubtopicId = subtopicMenu.value;
                //    loadQuestionsToAddExplanationForm(selectedSubtopicId);
                //}) 
            }
                
        }else{           
            clearMessages();
            // errors
            let add_explanation_msg = document.getElementById('add-explanation-msg');
            add_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;   
        } 
    }) 
    .catch(error => console.error('Failed to retrieve subtopics:', error));  
}

function loadQuestionsToAddExplanationForm() {
    const subtopicMenu = document.getElementById('subtopic-for-add-explanation');
    const selectedSubtopicId = subtopicMenu.value;
    const questionMenu = document.getElementById('question-for-add-explanation');
    const addExplanationMsg = document.getElementById('add-explanation-msg');
    
    // Clear existing messages and options
    if (addExplanationMsg) addExplanationMsg.innerHTML = '';
    questionMenu.innerHTML = '';

    const route = `/management/portal/load_questions_without_explanation/${selectedSubtopicId}`;

    fetch(route)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add placeholder option
                placeholderOption = placeholderDefaultOption();
                questionMenu.appendChild(placeholderOption);

                // Add new question options
                data.questions_without_explanation.forEach(question => {
                    const option = document.createElement('option');
                    option.value = question.id;
                    option.textContent = question.text;
                    questionMenu.appendChild(option);
                });

                // Check if there are valid questions
                const hasValidQuestions = questionMenu.options.length > 1;
                if (!hasValidQuestions) {
                    clearMessages();
                    displayMessage(
                        'There was a problem retrieving questions for the chosen subtopic',
                        'info'
                    );
                } else {
                    // Remove any existing 'change' event listeners
                    //const newQuestionMenu = questionMenu.cloneNode(true); 
                    //questionMenu.parentNode.replaceChild(newQuestionMenu, questionMenu);

                    // Add a new event listener
                    //newQuestionMenu.addEventListener('change', function () {
                    //    const selectedQuestionId = newQuestionMenu.value;
                    //    loadChoicesToAddExplanationForm(selectedQuestionId);
                    //});

                    // Update the reference
                    //questionMenu = newQuestionMenu;
                }
            } else {
                clearMessages();
                // errors
                let add_explanation_msg = document.getElementById('add-explanation-msg');
                add_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;   
            }
        })
        .catch(error => console.error('Failed to load questions:', error));
}

function loadChoicesToAddExplanationForm(){
    const questionMenu = document.getElementById('question-for-add-explanation');
    const selectedQuestionId = questionMenu.value;
    const addExplanationTextArea = document.getElementById('text-for-add-explanation');

    // get all the questions for the chosen subtopic
    const route = `/management/portal/load_choices/${selectedQuestionId}`;

    fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            choiceForms = data.choice_forms;
            // Insert the choice forms HTML into the choices-container
            document.getElementById('choices-container').innerHTML = data.choice_forms;

            // choice fields shouldn't be editable
            const choiceFields = document.querySelectorAll('.choice-fields input, .choice-fields textarea, .choice-fields select');
    
            choiceFields.forEach(function(field) {
                field.setAttribute('disabled', true);  
            });

            // enable the textarea
            addExplanationTextArea.removeAttribute('disabled');
            addExplanationTextArea.focus();
            addExplanationTextArea.value = '';

        }else{
            clearMessages();
            // errors
            let add_explanation_msg = document.getElementById('add-explanation-msg');
            add_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;   
        }
    })
    .catch(error => console.error('Failed to load answer choices for this question:', error));
}

function addExplanation(){
    const topicMenu = document.getElementById('topic-for-add-explanation');
    const add_explanation_msg = document.getElementById('add-explanation-msg');
    const addExplanationTextArea = document.getElementById('text-for-add-explanation');

    const route = `/management/portal/add_explanation`;

    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            // question form values
            question_id : document.getElementById('question-for-add-explanation').value,
            explanation_text : document.getElementById('text-for-add-explanation').value,  
        })
    })   
    .then(response => response.json())
    .then(data => {        
                
        if (data.success){ 
            document.getElementById('add-explanation-form').reset(); // reset the form
            document.getElementById('choices-container').innerHTML = '';
            addExplanationTextArea.setAttribute('disabled', 'disabled');
            addExplanationTextArea.value = '';

            topicMenu.innerHTML = '';
            // Add placeholder option for topic menu
            placeholderOption = placeholderDefaultOption();
            topicMenu.appendChild(placeholderOption); 

            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                topicMenu.appendChild(option);
            }); 

            const validTopicOptions = topicMenu.options.length > 1;

            if (!validTopicOptions){
               
                if (add_explanation_msg){
                    add_explanation_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }else{
                clearMessages();            
                // display success message
                add_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            }
            
        } else {
            // errors
            clearMessages();
            let add_explanation_msg = document.getElementById('add-explanation-msg');
            add_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
    })
    .catch(error => console.error('Error submitting the form', error));
}

function selectTopicForEditExplanation(){
    const topicMenu = document.getElementById('topic-for-edit-explanation');
    const subtopicMenu = document.getElementById('subtopic-for-edit-explanation');
    
    if (topicMenu){
        // must be at least one valid topic
        const validTopicOptions = topicMenu.options.length > 1;

        if (!validTopicOptions){
            displayMessage('There are no topics available.', 'info');
            return;
        }
       
        const selectedTopicId = topicMenu.value;       
        if (!selectedTopicId){
            displayMessage('There are no topics available.', 'info');
            return;
        } else{  
                        
            getSubtopicsForEditExplanation(selectedTopicId, subtopicMenu);
        }      
    }
}

function getSubtopicsForEditExplanation(selectedTopicId, subtopicMenu){
    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics_with_questions_with_explanations/${selectedTopicId}`;
    fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            // clear the existing subtopic options
            subtopicMenu.innerHTML = '',
        
            // load the new subtopics, including the placeholder option
            placeholderOption = placeholderDefaultOption();
            subtopicMenu.appendChild(placeholderOption);

            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                subtopicMenu.appendChild(option);
            }); 
            
            const validSubtopicOptions = subtopicMenu.options.length > 1;

            if (!validSubtopicOptions){
                let edit_explanation_msg = document.getElementById('edit-explanation-msg');
                if (edit_explanation_msg){
                    edit_explanation_msg.innerHTML = '';
                }
                clearMessages();
                displayMessage('There are no available subtopics for the chosen topic', 'info');
                return;
            }

        }else{
            // errors
            clearMessages();
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;   
        } 
    })    
}

function loadQuestionsToEditExplanationForm() {
    const subtopicMenu = document.getElementById('subtopic-for-edit-explanation');
    const selectedSubtopicId = subtopicMenu.value;
    const questionMenu = document.getElementById('question-for-edit-explanation');
    const editExplanationMsg = document.getElementById('edit-explanation-msg');
    
    // Clear existing messages and options
    if (editExplanationMsg){ 
        editExplanationMsg.innerHTML = '';
    }
    questionMenu.innerHTML = '';

    const route = `/management/portal/load_questions_with_explanation/${selectedSubtopicId}`;

    fetch(route)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add placeholder option
                placeholderOption = placeholderDefaultOption();
                questionMenu.appendChild(placeholderOption);

                // Add new question options
                data.questions_with_explanation.forEach(question => {
                    const option = document.createElement('option');
                    option.value = question.id;
                    option.textContent = question.text;
                    questionMenu.appendChild(option);
                });

                // Check if there are valid questions
                const hasValidQuestions = questionMenu.options.length > 1;
                if (!hasValidQuestions) {
                    clearMessages();
                    displayMessage(
                        'There was a problem retrieving questions for the chosen subtopic',
                        'info'
                    );
                } 

            } else {
                clearMessages();
                if (data.messages && data.messages.length > 0) {
                    editExplanationMsg.innerHTML = `
                        <div class="alert alert-${data.messages[0].tags}" role="alert">
                            ${data.messages[0].message}
                        </div>
                    `;
                } else {
                    displayMessage(
                        'An unexpected error occurred while retrieving questions.',
                        'error'
                    );
                }
            }
        })
        .catch(error => {
            console.error('Error loading questions:', error);
            clearMessages();
            displayMessage('Failed to load questions. Please try again later.', 'error');
        });
}

function loadChoicesToEditExplanationForm(){
    const questionMenu = document.getElementById('question-for-edit-explanation');
    const selectedQuestionId = questionMenu.value;
    // get all the questions for the chosen subtopic
    const route = `/management/portal/load_choices/${selectedQuestionId}`;

    fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            choiceForms = data.choice_forms;
            // Insert the choice forms HTML into the choices-container
            document.getElementById('choices-container').innerHTML = data.choice_forms;

            // choice fields shouldn't be editable
            const choiceFields = document.querySelectorAll('.choice-fields input, .choice-fields textarea, .choice-fields select');
    
            choiceFields.forEach(function(field) {
            field.setAttribute('disabled', true);  
            });

        }else{
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            if (edit_explanation_msg){
                edit_explanation_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There was a problem retrieving choices for this question', 'info');
            return;
        }
    })
}

function getExplanationForQuestion(){
    const questionMenu = document.getElementById('question-for-edit-explanation');
    const selectedQuestionId = questionMenu.value;
    const explanationTextArea = document.getElementById('text-for-edit-explanation');
    
    // get the explanation for the chosen question
    const route = `/management/portal/get_explanation/${selectedQuestionId}`;

    fetch(route)
    .then(response => response.json())
    .then(data =>{
        if (data.success){
            // clear the textbox
            document.getElementById('explanation-container').style.display = 'block';
            explanationTextArea.removeAttribute('disabled');
            explanationTextArea.innerHTML = '';

            // load the textbox with the explanation
            explanationTextArea.textContent = data.explanation_text;
            const explanationId = document.getElementById('explanation-id');
            explanationId.value = data.explanation_id;

            // enable the buttons
            document.getElementById('edit-explanation-btn').disabled = false;
            document.getElementById('delete-explanation-btn').disabled = false;
            
        }else{
            // errors
            document.getElementById('explanation-container').style.display = 'none';
            document.getElementById('edit-explanation-btn').disabled = true;
            document.getElementById('delete-explanation-btn').disabled = true;
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;

        }
    })
    .catch(error => console.error('Error retrieving explanation', error));
}

function editExplanation(){
    const explanationTextArea = document.getElementById('text-for-edit-explanation');
    const route = `/management/portal/edit_explanation`;

    // Retrieve the django CSRF token from the form
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(route, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            // question form values
            explanation_id : document.getElementById('explanation-id').value,
            explanation_text : document.getElementById('text-for-edit-explanation').value,  
        })
    })   
    .then(response => response.json())
    .then(data => {
        
        document.getElementById('delete-explanation-btn').disabled = true;
                
        if (data.success){ 
            document.getElementById('edit-explanation-form').reset(); // reset the form 
            clearMessages();
            document.getElementById('text-for-edit-explanation').innerHTML = '';
            document.getElementById('choices-container').innerHTML = '';
            explanationTextArea.setAttribute('disabled', 'disabled');

            // display success message
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            
        } else {
            // errors
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
        }
    })
    .catch(error => console.error('Error submitting the form', error));
}

function setupDeleteExplanationDialog(){    
    const dialogElement = document.getElementById('confirm-delete-explanation-dialog');

    if (dialogElement){        
        dialogElement.showModal();
    }else {
        console.error('Dialog element with ID confirm-delete-explanation-dialog not found.');
        return; 
    }
}

function cancelExplanationDialog(){
    const dialogElement = document.getElementById('confirm-delete-explanation-dialog');
    dialogElement.close();
}

function setupDeleteExplanationModal(){
    const selectExplanationToDelete = document.getElementById('text-for-edit-explanation');
    const deleteExplanationButton = document.getElementById('delete-explanation-btn');
    const modalElement = document.getElementById('confirm-delete-explanation-modal');

    if (modalElement){
        if (!selectExplanationToDelete){
            displayMessage('There is no explanation for this question.', 'info');  
            return;  // No further setup needed if there is no explanation               
        } 
        // Check if the delete button exists before setting properties
        if (!deleteExplanationButton) {
            return;  // Early exit to avoid further errors
        }  

        // instantiate the confirmation modal
        const confirmDeleteExplanationModal = new bootstrap.Modal(document.getElementById('confirm-delete-explanation-modal'), {});
                         
        // Show the modal when the delete button is clicked
        deleteExplanationButton.addEventListener('click', function() {            
            confirmDeleteExplanationModal.show();           
        }); 
                                      
        deleteExplanation(confirmDeleteExplanationModal);  
        
    }

}

function deleteExplanation(){ 
    const dialogElement = document.getElementById('confirm-delete-explanation-dialog');
    const explanationTextArea = document.getElementById('text-for-edit-explanation');   
          
    // Fetch the explanation ID at the time of button click
    const explanationId = document.getElementById('explanation-id').value;                                  

    const route = `/management/portal/delete_explanation/${explanationId}`;

    // Retrieve the django CSRF token from the form
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(route, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },        
    })
    .then(response => response.json())
    .then(data => {                
        if (data.success){
            document.getElementById('edit-explanation-form').reset(); // reset the form
            
            explanationTextArea.innerHTML = '';
            explanationTextArea.setAttribute('disabled', 'disabled');
            document.getElementById('choices-container').innerHTML = '';
            document.getElementById('delete-explanation-btn').disabled = true;
            
            // display success message
            clearMessages();
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            dialogElement.close();
            
        }else{
            // errors
            document.getElementById('delete-explanation-btn').disabled = true;
            let edit_explanation_msg = document.getElementById('edit-explanation-msg');
            edit_explanation_msg.innerHTML = `<div class="alert alert-${data.messages[0].tags}" role="alert">${data.messages[0].message}</div>`;
            dialogElement.close();
        }

    })
    .catch(error => console.error('Explanation deletion failed:', error));
    dialogElement.close();   
}  

// Helper functions

function placeholderDefaultOption(){
    const placeholderOption= document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = '--------';
    placeholderOption.selected = true;
    return placeholderOption;
}

function getSubtopics(selectedTopicId, subtopicMenu, callback){
    // get the subtopics for the chosen topic to populate the subtopics dropdown menu
    const route = `/management/portal/get_subtopics/${selectedTopicId}`;
    
    fetch(route)
    .then(response => response.json())
    .then(data =>{
        
        if (data.success){
            // clear the existing subtopic options
            subtopicMenu.innerHTML = '';
           
            // load the new subtopics, including the placeholder option
            //subtopicMenu.innerHTML = '<option value="" selected ="">--------</option>';
            placeholderOption = placeholderDefaultOption();
            subtopicMenu.appendChild(placeholderOption);
            data.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic.id;
                option.textContent = subtopic.name;
                subtopicMenu.appendChild(option);
            }); 
            
            const validSubtopicOptions = subtopicMenu.options.length > 1;

                if (!validSubtopicOptions){
                    let add_question_and_choices_msg = document.getElementById('add-question-and-choices-msg');
                    if (add_question_and_choices_msg){
                        add_question_and_choices_msg.innerHTML = '';
                    }
                    clearMessages();
                    displayMessage('There are no available subtopics for the chosen topic', 'info');
                    return;
                }else{
                    if (callback){
                        callback();
                    }
                }
        }else{
            let add_question_and_choices_msg = document.getElementById('add-question-and-choices-msg');
            if (add_question_and_choices_msg){
                add_question_and_choices_msg.innerHTML = '';
            }
            clearMessages();
            displayMessage('There are no available subtopics for the chosen topic', 'info');
            return;    
        } 
    })

}

function hideSidebarMenus(){
    // This function clears any existing sidebar menus before loading a new one

    const sidebarMenus = document.querySelectorAll('.sidebar-menu');
    if (sidebarMenus.length > 0){
        sidebarMenus.forEach(sidebarMenu =>{
            sidebarMenu.style.display = 'none';
        });
    }
}

function displayMessage(message, type) {
    const messageContainer = document.querySelector('.error-msg');
    if (messageContainer) {
        // Clear any existing messages
        messageContainer.innerHTML = '';

        // insert the new message
        messageContainer.insertAdjacentHTML('beforeend', `<div class="alert alert-${type}" role="alert">${message}</div>`);
    }
}

function clearMessages(){
    const messageContainer = document.querySelector('.error-msg');
    const messageDiv = document.querySelector('.msg-div');
    if (messageContainer) {
        // Clear any existing messages
        messageContainer.innerHTML = '';
    }
    if (messageDiv) {
        // Clear any existing messages
        messageDiv.innerHTML = '';
    }
}

function updatePagination(newPageNumber){
    const topicId = document.getElementById('topic-id').value;
    const subtopicId = document.getElementById('subtopic-id').value;
    const pageNumber = newPageNumber || document.getElementById('page').value; // Use new page number if provided;
    const route = `/management/portal/edit_all_questions_and_choices/?topic=${topicId}&subtopic=${subtopicId}&page=${pageNumber}`;

    fetch(route)
    .then(response => response.text())
    .then(html => {
        document.getElementById('edit-all-questions-and-choices-container').innerHTML = html;
        initializePage(); // Re-initialize the page after loading new content
    })
    .catch(error => console.error('Error loading updated content:', error));
}

function changeWelcomeMessageBasedOnScreenSize(){
    const screenWidth = window.innerWidth;
    const welcomeMessage = document.getElementById('welcome-message');

    if (welcomeMessage){
        welcomeMessage.innerHTML = '';
        
        if (screenWidth < 576){
            welcomeMessage.innerHTML = 
            'To manage your quiz database, click on the appropriate menu in the top navigation bar.'; 
        } else {
            welcomeMessage.innerHTML = 
            'To manage your quiz database, you may click on the appropriate menu in the top navigation bar.\
            Questions and answer choices may also be managed from the sidebar.'        
        }
    }
}
