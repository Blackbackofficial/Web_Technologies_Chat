# Terms of reference for creating a chat
As a task, it is proposed to complete the project "Questions and Answers". This service will allow Internet users to ask questions and receive answers to them. Commenting and voting capabilities build a community and allow users to actively help others. The recommended implementation is [Stack Overflow](https://stackoverflow.com).

## Technologies used
- Application code is written in **Python + Django**.
- The application runs under the control of the **Gunicorn** server.
- Database - **PostreSQL**.
- **nginx** is used to return statics.
- To deliver real-time messages **nginx + mod_push**.
- For data caching - **memcached**.
- Layout is done using **Twitter Bootstrap**.
- Interface interaction with the user is provided by **JavaScript/jQuery**.
- You can use the **django.contrib.auth** application to authorize and store users.

## Main entities
- User - email, nickname, password, avatar, date of registration, rating.
- Question - title, content, author, creation date, tags, rating.
- Answer - content, author, date of writing, flag of the correct answer, rating.
- Tag - tag word.

## Basic pages and forms
1. **Listing questions** with pagination of 20 questions per page. It is necessary to implement sorting by date added and rating (2 types of sorting). The site header contains: a logo, a search bar (for quick search by the title and content of the question), a button to ask a question (only available to authorized users). On the right side of the header is a user block. For an authorized user, the user block contains his nickname, avatar, links to the “exit” and to the page with his profile. For unauthorized - links "login" and "registration". In the right column - information blocks "Popular tags" and "Top users" (description below). All listings have “like/dislike” buttons that allow you to change the rating of a question.

2. **Page for adding a question** (can be done as an overlay). Available only to authorized users. The title, question text and tags are entered into the form, separated by commas. A question can have no more than 3 tags associated with it. For a hint when choosing a tag, you can use a ready-made jquery plugin. Ready-made django applications for tags are not allowed. When processing the form, it is necessary to check the validity of the data. If the question is successfully added, the user is redirected to the question page, if there are errors, they must be displayed in the form.

3. **Question page with a list of answers**. You can add an answer on the question page. Answers are sorted by rating and date of addition if the rating is equal. Answers are divided into 30 pieces per page. The form for adding an answer is on the question page. Displayed only for authorized users. After adding an answer, the questioner should receive an email notification of the new answer. This letter should contain a link to go to the question page. The author of the question can mark one of the answers as correct. Users can vote for questions and answers with likes "+" or "-". One user can vote for 1 question and answer only 1 time, but can cancel his choice or re-vote an unlimited number of times.

4. **Listing questions by tag**. This page displays all questions containing some tag. Sort by question rating. Pagination of 20 questions. Users get to this page by clicking on one of the tags in the question description.

5. **User's page** contains his settings - email, nick and profile picture. Each user can only view their own page. The user should be able to change email, nick and profile picture.


6. **Authorization form**. Consists of the username and password fields. Additionally, there is a link to the registration form. If authorization is successful, the user is redirected to the original page; if authorization is unsuccessful, form error messages are displayed in the form. For authorized users, instead of this form, the “Logout” button should be shown.

7. **Registration page**. Any user can register on the site by filling out the form with e-mail, nickname, avatar and password. The avatar is uploaded to the server and displayed next to the user's questions and answers. If the registration in the form fails, you should display error messages.

8. **Block of popular tags**. In the right column of the site is a cloud of the 20 most popular tags. The most popular tags are those that have been used in the most questions. The generation of this block takes a long time, so this block must be generated in the background using a cron script.

9. **Block of top users** (weeks). The top users block includes 10 authors who have asked the most popular questions or answers over the past week. Those. questions and answers created in the last week are sorted by rating. We choose the top N, their authors will be the “best”.

## Project requirements
1. The structure of the project should be clear to users. Pages are navigated through links. Form processing should be done with a redirect.
2. The project code should be neat and without duplication. The presence of large repetitive code snippets or patterns may be the reason for the deduction of points.
3. The layout of the project must be done using css framework Twitter Bootstrap.
4. The application code should be sensitive to the input data and issue appropriate error codes and texts. Message to users "Question added",
"The question was not added because" is displayed in the overlay. A server response with a 500 code may be the reason for the deduction.
5. Page generation time should not depend on the amount of data in the database.
6. Project pages should not be given more than 1 second.

## Data volume requirements
- Users > 10,000.
- Questions > 100,000.
- Answers > 1,000,000.
- Tags > 10,000.
- User ratings > 2,000,000.
