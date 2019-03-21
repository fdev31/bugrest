// compute content index
document.querySelector('.document').childNodes.forEach( (e, i) => {if(e.id == 'header_limit') CONTENT_INDEX=i+1})

window.run_filter = function() {
    let name = document.querySelector('#filter_name').value;
    let value = document.querySelector('#filter_value').value;
    filterElements(name, value);
}
window.filterElements = function(name, value) {
    let sections = document.querySelectorAll('.section');
    let fields = new Array(... sections).map(e=> new Array(... e.querySelectorAll('tr.field')).filter(e=>!!e && e.querySelector('.field-name').textContent == name)[0])
    fields.forEach( e=> {
        e.parentNode.parentNode.parentNode.style.display = (e.querySelector('.field-body').textContent == value)?'block':'none'
    })
}

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
    let header = new Array(... document.querySelector('.document').childNodes).slice(0, CONTENT_INDEX).map(e => e.outerHTML).join('')
    document.querySelector('.document').innerHTML = header + ordered_html
}

document.addEventListener("DOMContentLoaded", (e) => {
    let options = [];
    let opts_parsed = new Set();
    for (let elt of document.querySelectorAll('.section')) {
        for (let e of elt.querySelectorAll('.field-name')) {
            opts_parsed.add(e.textContent);
        }
    }
    opts_parsed.forEach((e)=> {
        options.push(`<option value="${e}">${e}</option>`)
    })
    document.querySelector('#filter_name').innerHTML = options.join('\n');
    document.querySelectorAll('.filter_input').forEach(e=> (addEventListener('keydown', (e)=> (e.keyCode == 13 && run_filter()))));
})
