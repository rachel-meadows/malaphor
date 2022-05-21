function changeProfanityFilterQuery(event) {
  console.log(event)
  // this.form.submit()
}

function showInputField() {
  console.log('running')
  document.getElementById('user-input-field').style.display = 'block'
}

document
  .getElementById('profanity-filter')
  .addEventListener('click', (event) => {
    if (document.getElementById('profanity-filter').checked) {
      console.log('checked')
    } else {
      console.log('unchecked')
    }
  })
