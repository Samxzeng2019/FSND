window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// delete to do item with button X for venues
const venue_buttons = document.querySelectorAll('.delete-button-venue');
for (let j=0; j<venue_buttons.length; j++) {
    const venue_button = venue_buttons[j]
    venue_button.onclick = e => {
        console.log("event", e)
        const venue_id = e.target.dataset['id']

        fetch('venues/'+ venue_id, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then((data) => {
            button_id = "delete-button-venue"+venue_id
            console.log(data['success'])
            if (data['success']) {
                document.getElementById(button_id).style.color = "green"
                document.getElementById(button_id).innerHTML = "&check; Item deleted successfully"
                console.log('delete this item', button_id)
            } else {
                document.getElementById(button_id).innerHTML = "&cross; Delete ussuccessful"
                console.log(data)
            }
        })
        .catch(() => {
            document.getElementById(button_id).innerHTML = 'There is an error occured'
        })
    }
}

// delete to do item with button X for artists
const artist_buttons = document.querySelectorAll('.delete-button-artist');
for (let j=0; j<artist_buttons.length; j++) {
    const artist_button = artist_buttons[j]
    artist_button.onclick = e => {
        console.log("event", e)
        const artist_id = e.target.dataset['id']

        fetch('artists/'+ artist_id, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then((data) => {
            button_id = "delete-button-artist"+artist_id
            console.log(data['success'])
            if (data['success']) {
                document.getElementById(button_id).style.color = "green"
                document.getElementById(button_id).innerHTML = "&check; Item deleted successfully"
                console.log('delete this item', button_id)
            } else {
                document.getElementById(button_id).innerHTML = "&cross; Delete ussuccessful"
                console.log(data)
            }
        })
        .catch(() => {
            document.getElementById(button_id).innerHTML = 'There is an error occured'
        })
    }
}

// delete to do item with button X for shows
const show_buttons = document.querySelectorAll('.delete-button-show');
for (let j=0; j<show_buttons.length; j++) {
    const show_button = show_buttons[j]
    show_button.onclick = e => {
        console.log("event", e)
        const show_id = e.target.dataset['id']
        console.log(e.target.dataset['id'])
        fetch('shows/'+ show_id, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then((data) => {
            button_id = "delete-button-show"+show_id
            console.log(data['success'])
            if (data['success']) {
                document.getElementById(button_id).style.color = "green"
                document.getElementById(button_id).innerHTML = "&check; Item deleted successfully"
                console.log('delete this item', button_id)
            } else {
                document.getElementById(button_id).innerHTML = "&cross; Delete ussuccessful"
                console.log(data)
            }
        })
        .catch(() => {
            document.getElementById(button_id).innerHTML = 'There is an error occured'
        })
    }
}