$(function() {
    $('.dropdown').on('click', function() {
        let content = this.parentNode.parentNode.children[1]
        if(content.style.display === "") {
            content.style.display = "none"
            this.style.transform = "rotateZ(90deg)"
        } else {
            content.style.display = ""
            this.style.transform = "rotateZ(0)"
        }
    })
})
