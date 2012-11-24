var dropArea;

function abortEvent(e) {
	e.preventDefault();
	e.stopPropagation();
}
function previewImage(file) {
	var img = document.createElement('img');
	document.body.appendChild(img);
	var reader = new FileReader();
	reader.onload = function(e) {
		img.src = e.target.result;
		img[img.width > img.height ? 'width':'height'] = 100;
	};
	reader.readAsDataURL(file);
}


function dropHandler(e) {
	e.preventDefault();
	e.stopPropagation();
	var files = e.dataTransfer.files;
	for (var i = 0; i < files.length; i++) {
		previewImage(files[i]);
		xhr = new XMLHttpRequest();
		xhr.open('post', '/photo', true);
		var formData = new FormData();
		formData.append('photo', files[i]);
		formData.append('tzoffset', (new Date()).getTimezoneOffset());
		xhr.send(formData);
	}
}
function dragEnterHandler(e) {
	dropArea.style.backgroundColor = 'red';
	abortEvent(e);
}
function dragLeaveHandler(e) {
	if (e.target == dropArea) {
		dropArea.style.backgroundColor = 'transparent';
	}
	abortEvent(e);
}


$(function() {
	dropArea = $('#drop-area')[0];
	dropArea.addEventListener('drop', dropHandler, false);
	dropArea.addEventListener('dragover', abortEvent, false);
	dropArea.addEventListener('dragenter', dragEnterHandler, false);
	dropArea.addEventListener('dragleave', dragLeaveHandler, false);
});
