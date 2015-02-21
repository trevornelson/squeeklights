	
function convertTimestamp() {
	// get date and time selections
	var date_input = $('#date').val();
	var time_input = $('#time').val();
	var date_time = date_input + " " + time_input

	console.log(date_time);

	// convert to unix timestamp as start_timestamp

	var unixtime = Date.parse(date_time).getTime()/1000
	var start_timestamp = unixtime + 14400  // adjusts for est timezone

	// add to start_timestamp for end_timestamp
	var end_timestamp = start_timestamp + 14400 // adds 4 hours in timestamp

	// convert start_timestamp and end_timestamp to string
	var start_timestamp_str = String(start_timestamp);
	var end_timestamp_str = String(end_timestamp);

	// add to hidden POST form fields
	$('start_timestamp').val(start_timestamp_str);
	$('end_timestamp').val(end_timestamp_str);
	console.log(start_timestamp_str);
	console.log(end_timestamp_str);
	document.getElementById('start_timestamp').value = start_timestamp_str;
	document.getElementById('end_timestamp').value = end_timestamp_str;

	// submits form
	$('#venue_form').submit();

}



