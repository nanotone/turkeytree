var $dropArea;

function abortEvent(e) {
	e.preventDefault();
	e.stopPropagation();
}

function formatDate(date) {
	var pad2Digits = function(n) { return String(100 + n).substr(1); };
	var hour = date.getUTCHours();
	return (String(date.getUTCFullYear()) + "-" + (date.getUTCMonth() + 1) + "-"
		+ date.getUTCDate() + " " + ((hour + 11) % 12 + 1) + ":"
		+ pad2Digits(date.getUTCMinutes()) + ":" + pad2Digits(date.getUTCSeconds())
		+ " " + (hour < 12 ? 'am':'pm'));
}

function previewImage(file) {
	var fileid;
	var $thumbContainer = $('<div class="upload-thumb"><img /><div class="progressbar"></div><div class="time"></div></div>');
	var $img = $thumbContainer.children('img');

	$('body').append($thumbContainer);
	var reader = new FileReader(); // transforms the image into a data url
	reader.onload = function(e) {
		$img.attr('src', e.target.result);
		$thumbContainer[$img.width() > $img.height() ? 'width':'height'](150); // voodoo.
	};
	reader.readAsDataURL(file);

	var xhr = new XMLHttpRequest();
	xhr.open('post', '/photo', true);

	var progressHandler = function(e) {
		var position = e.position || e.loaded;
		var total = e.totalSize || e.total;
		var percent = position/total * 100;
		$thumbContainer.children('.progressbar').width((100-percent) + '%');
	};
	var readyStateHandler = function() {
		if (xhr.readyState == 4) {  // http response has finished loading
			var response = JSON.parse(xhr.responseText);
			fileid = response._id;
			$thumbContainer.width(response.tn_size[0]);
			$thumbContainer.height(response.tn_size[1]);
			$img.attr('src', '/' + response.tn);  // make this less hackish?
			var date = new Date(response.time.naive * 1000);
			$thumbContainer.children('.time').text(formatDate(date));
			var $fileids = $('#fileids');
			$fileids.val($fileids.val() + ' ' + fileid);
			$('#submit-button').show();
		}
	};

	(xhr.upload || xhr).addEventListener('progress', progressHandler);
	xhr.onreadystatechange = readyStateHandler;

	var formData = new FormData();
	formData.append('photo', file);
	xhr.send(formData);
}


function dropHandler(e) {
	abortEvent(e);
	var files = e.dataTransfer.files;
	for (var i = 0; i < files.length; i++) {
		previewImage(files[i]);
	}

	$dropArea.removeClass('dragover');
}
function dragEnterHandler(e) {
	$dropArea.addClass('dragover');
	abortEvent(e);
}
function dragLeaveHandler(e) {
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
