document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#follow-form').onsubmit = follow_user;
    document.querySelectorAll('#edit-post').forEach((editButton) => {
        editButton.onclick = edit_post;
    })
    document.querySelectorAll('#like-button').forEach((likeButton) => {
        likeButton.onclick = like_post;
    })
})

function follow_user() {
    const button = document.querySelector('#follow-button')
    const val = button.innerHTML.trim()
    const name = document.querySelector('#follow-user').innerHTML.trim()
    fetch('/follow', {
        method: 'POST',
        body: JSON.stringify({
            value: val,
            username: name
        })
    })
    .then(response => response.json())
    .then(result => {
        const follower = document.querySelector("#follower-count")
        let count = parseInt(follower.innerHTML)
        if (val === "Follow") {
            button.innerHTML = "Unfollow"
            follower.innerHTML = ++count;
        }
        else {
            button.innerHTML = "Follow"
            follower.innerHTML = --count;
        }
        display_post_alert(result, val)
    })
    return false;
}

function display_post_alert(result, val) {
    let ele = document.createElement('div')
    ele.id = "post-alert"
    ele.style.animationPlayState = 'paused';
    if (result.hasOwnProperty('error')) {
        ele.className = "alert alert-danger alert-animated"
        ele.innerHTML = result.error
    }
    else {
        ele.className = "alert alert-primary alert-animated"
        ele.innerHTML = val + "ed Successfully!"
    }
    document.querySelector('#follow-user').insertAdjacentElement("beforebegin", ele)
    ele.style.animationPlayState = 'running'
    ele.addEventListener('animationend', () => {
        ele.remove();
    })
}

function display_post(result) {
    let card = document.createElement('div')
    card.className = "card card-animated"
    card.style.animationPlayState = "paused"

    let card_body = document.createElement('div')
    card_body.className = "card-body"

    let card_id = document.createElement('span')
    card_id.style.display = "none"
    card_id.id = "post-id"
    card_id.innerHTML = result.result.id

    let card_title = document.createElement('h5')
    card_title.className = "card-title"
    const username = result.result.username
    card_title.innerHTML = `<a href="{% url 'reuser' ${username} %}">${username}</a>`
    
    let card_text = document.createElement('p')
    card_text.className = "card-text"
    card_text.id = "post-text"
    card_text.innerHTML = result.result.text

    let card_time = document.createElement('h6')
    card_time.className = "card-subtitle text-muted"
    card_time.innerHTML = result.result.time

    let like_button = document.createElement('button')
    like_button.style.color = "red";
    like_button.id = "like-button"

    let like_icon = document.createElement('i')
    like_icon.className = "fa fa-heart-o"

    let card_likes = document.createElement('small')
    card_likes.className = "text-muted"
    card_likes.innerHTML = result.result.likes

    like_button.append(like_icon)

    card_body.append(card_id)
    card_body.append(card_title)
    card_body.append(card_text)
    card_body.append(card_time)
    card_body.append(like_button)
    card_body.append(card_likes)

    if (result.current_user == result.result.username) {
        let edit_button = document.createElement('button')
        edit_button.className = "btn btn-sm btn-primary"
        edit_button.id = "edit-post"
        edit_button.innerHTML = "Edit Post"
        edit_button.onclick = edit_post
        card_body.append(edit_button)
    }

    card.append(card_body)
    document.querySelector('#title').insertAdjacentElement('afterend', card)
    card.style.animationPlayState = "running"
    card.addEventListener('animationend', () => {
        card.style.animationPlayState = "paused"
        card.style.marginBottom = "8px";
    })
}

function edit_post() {
    const content = this.previousElementSibling.previousElementSibling.previousElementSibling.innerHTML;
    let node = this.previousElementSibling
    do {
        node = node.previousElementSibling;
    } while (node.id != "post-id")
    const post_id = node.innerHTML
    let card = this.parentNode
    card.innerHTML = ""

    let text = document.createElement('textarea')
    text.cols = 40
    text.rows = 5
    text.placeholder = "Edit post"
    text.className = "form-control w-50 rounded"
    text.style.resize = "none"
    text.maxLength = 280
    text.required = true
    text.innerHTML = content

    let button = document.createElement('button')
    button.className = "btn btn-sm btn-primary"
    button.type = "submit"
    button.innerHTML = "Edit Post"

    card.append(text)
    card.append(button)

    button.onclick =  () => {
        const newtext = text.value
        fetch('/editpost', {
            method: 'POST',
            body: JSON.stringify({
                id: post_id,
                text: newtext
            })
        })
        .then(response => response.json())
        .then(result => {
            card.parentNode.remove()
            window.scrollTo(0,0);
            display_post_alert(result);
            display_post(result);
        })
    }
}

function like_post() {
    let button = this
    let node = this.previousElementSibling
    do {
        node = node.previousElementSibling;
    } while (node.id != "post-id")
    const post_id = node.innerHTML
    fetch('/likepost', {
        method: "POST",
        body: JSON.stringify({
            id: post_id
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.hasOwnProperty('error')) {
            console.log(result.error)
        }

        let icon = button.firstElementChild;
        let likes = button.nextElementSibling
        let count = parseInt(likes.innerHTML)

        if (icon.className === "fa fa-heart-o") {
            icon.className = "fa fa-heart"
            likes.innerHTML = ++count;
        }
        else if (icon.className === "fa fa-heart") {
            icon.className = "fa fa-heart-o"
            likes.innerHTML = --count;
        }
    })
    return false;
}