var $dropArea;

function abortEvent(e) {
	e.preventDefault();
	e.stopPropagation();
}

function previewImage(file, i) {
	var $thumbContainer = $('<div class="upload-thumb" id="thumb"' + i + '"><img /><div class="progressbar"></div></div>');
	var $img = $thumbContainer.children('img');

	$('body').append($thumbContainer);
	var reader = new FileReader(); // transforms the image into a data url
	reader.onload = function(e) {
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
	    var percent = position/total * 100;


	    
	    $thumbContainer.children('.progressbar').width((100-percent) + '%');
	});

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {  // http response has finished loading
			var response = JSON.parse(xhr.responseText);
			$thumbContainer.width(response.tn_size[0]);
			$thumbContainer.height(response.tn_size[1]);
			$img.attr('src', '/' + response.tn);  // make this less hackish?
		}
	};

	xhr.send(formData);
}


function dropHandler(e) {
	e.preventDefault();
	e.stopPropagation();
	var files = e.dataTransfer.files;
	for (var i = 0; i < files.length; i++) {
		previewImage(files[i], i);
	}

	$dropArea.removeClass('dragover');
}
function dragEnterHandler(e) {
	$dropArea.addClass('dragover');
	abortEvent(e);
}
function dragLeaveHandler(e) {
	console.log("leaving");
	if (e.target == $dropArea[0]) {
		$dropArea.removeClass('dragover');
	}
	abortEvent(e);
}


$(function() {
	$dropArea = $('#drop-area');
	$dropArea[0].addEventListener('drop', dropHandler, false);
	$dropArea[0].addEventListener('dragover', abortEvent, false);
	$dropArea[0].addEventListener('dragenter', dragEnterHandler, false);
	$dropArea[0].addEventListener('dragleave', dragLeaveHandler, false);
});
