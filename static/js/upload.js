var dropArea;

function abortEvent(e) {
	e.preventDefault();
	e.stopPropagation();
}

function previewImage(file, i) {
	var $thumbContainer = $('<div class="upload-thumb" id="thumb"' + i + '"><img /><div class="progressbar"></div></div>');
	$('body').append($thumbContainer);
	var reader = new FileReader(); // transforms the image into a data url
	reader.onload = function(e) {
		var $img = $thumbContainer.children('img');
		$img.attr('src', e.target.result);
		$thumbContainer[$img.width() > $img.height() ? 'width':'height'](150); // voodoo.
	};
	reader.readAsDataURL(file);

	xhr = new XMLHttpRequest();
	xhr.open('post', '/photo', true);
	var formData = new FormData();
	formData.append('photo', file);
	//formData.append('tzoffset', (new Date()).getTimezoneOffset());

	var eventSource = xhr.upload || xhr;

	eventSource.addEventListener("progress", function(e) {
		 console.log("anything");

	    var position = e.position || e.loaded;
	    var total = e.totalSize || e.total;
	    var percent = position/total * 50;


	    
	    $thumbContainer.children('.progressbar').width(percent + '%');
	});

	xhr.send(formData);
}


function dropHandler(e) {
	e.preventDefault();
	e.stopPropagation();
	var files = e.dataTransfer.files;
	for (var i = 0; i < files.length; i++) {
		previewImage(files[i], i);
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
