window.sortElements = function(name) {
    let sections = document.querySelectorAll('.section');
    name = name + ":"
    let fields = new Array(... sections).map(e=> new Array(... e.querySelectorAll('tr.field')).filter(e=>e.querySelector('.field-name').textContent == name)[0])
    fields.sort( (a, b) => {
        let va = a.querySelector('.field-body').textContent;
        let vb = b.querySelector('.field-body').textContent;
        if (va > vb)
            return -1;
        if (va < vb)
            return 1;
        return 0
    } )
    let elements = fields.map(e => e.parentElement.parentElement.parentElement)
    let ordered_html = elements.map(e => e.outerHTML).join('')
    elements.forEach( e => e.outerHTML = '')
    let header = new Array(... document.querySelector('.document').childNodes).slice(0, 7).map(e => e.outerHTML).join('')
    document.querySelector('.document').innerHTML = header + ordered_html
}

// TODO: add a sorter dropdown on page load
