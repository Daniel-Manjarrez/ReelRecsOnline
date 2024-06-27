let iteration = 1;
let items = null;
let query = null;

function highlight(text, query) {
    // Escape special characters in the query to ensure it's safe for regex use
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    const re = new RegExp(`(${escapedQuery})`, 'gi'); // gi is case insensititve
    
    // Replace matching parts with <strong> tags to make them bold
    return text.replace(re, '<span class="highlight">$1</span>');
}



$(document).ready(function() {

    //console.log("Test " + iteration); // for testing purposes

    $('#search-form').on('submit', function(event) {
        const query = $('##searchInput').val().trim();

        if (query === '') {
            event.preventDefault(); // make sure form doesn't submit immediately

            $('#searchInput').val(''); // clear the input field
            $('#searchInput').focus(); // Focus the user's cursor back on the input field
        }
    });

    $(document).on('searchResultsLoaded', function() { // items filled in (by server), must have 0 or more elements
        console.log('searchResultsLoaded.');
        console.log(items);
        console.log(items.length);
        
        $('#resultsList').empty(); // clear anything existing
        
        $('#searchHeader').text(`Search results for "${query}"`);

        // indicate number of results returned
        if (items.length > 0) {
            $('#resultsCount').text(`${items.length} result(s) found`);
        }
        else {
            console.log("triggered");
            $('#resultsCount').text(`No matches found`);
        }

        var $container = $('#resultsList');
        var $row = $('<div class="row"></div>'); // Start with the first row

        if (items.length > 0) { // there are items returned
            // const boldedItems = items.map(item => highlight(item, query)); // apply highlight to each item first

            items.forEach(function(item, index) { // it's because we're transforming items, I'm guessing?

                // Highlight and join genres and actors
                const highlightedGenres = item.genres.map(genre => highlight(genre, query)).join(', ');
                const highlightedActors = item.actors.map(actor => highlight(actor, query)).join(', ');
                const highlightedTitle = highlight(item.title, query); // bold the match

                // $('#resultsList').append(`<li>${title}</li>`);

                // Create the card HTML for each item
                var $col = $('<div class="col-md-4 d-flex align-items-stretch"></div>');
                var cardHtml = 
                    '<div class="card mb-4" style="width: 100%;">' +
                        '<a href="/view/' + item.id + '">' +
                            '<img src="' + item.image + '" class="card-img-top" alt="' + item.title + '">' +
                        '</a>' +
                        '<div class="card-body d-flex flex-column">' +
                            '<h5 class="card-title">' + highlightedTitle + '</h5>' +
                            '<p class="card-text">Genres: ' + highlightedGenres + '</p>' +
                            '<p class="card-text">Actors: ' + highlightedActors + '</p>' +
                            '<a href="/view/' + item.id + '" class="btn btn-primary mt-auto">View Details</a>' +
                        '</div>' +
                    '</div>';
                $col.html(cardHtml);
                $row.append($col);

                // After every third item, append the row to the container and start a new row
                if ((index + 1) % 3 === 0) {
                    $container.append($row);
                    $row = $('<div class="row"></div>'); // Start a new row for the next set of items
                }

                // have it somewhere else

                // <li><a href="/view/${item.id}">${title}</a></li>
            });

            // After exiting the loop, append any remaining items in the last row to the container
            if (items.length % 3 !== 0) {
                $container.append($row);
            }
            
            /**
            items.forEach(function(item) {
                const title = highlight(item.title, query);
                $('#resultsList').append(`<li><a href="/view/${item.id}">${title}</a></li>`);
            });
            */
        }
            
        /**
        else {
            $('#resultsList').append('<li>No results found</li>');
        }
        */
    });

    // when the user tries to submit a new kdrama
    $('#addKdramaForm').submit(function(e) {
        e.preventDefault(); // Prevent the default form submission

        // Clear previous error states
        $('.form-control').removeClass('is-invalid'); // use the is-invalid class to highlight invalid inputs
        // this class is built into Bootstrap
        $('.success-message').remove(); // Remove existing success messages
        var isValid = true;

        // Validate Title
        if (!$('#title').val().trim()) { // is empty
            $('#title').addClass('is-invalid');
            isValid = false;
        }

        // Validate Image URL
        var imageUrl = $('#image').val().trim();
        if (!imageUrl || !imageUrl.match(/\.(jpeg|jpg|gif|png)$/i)) { // regex to make sure it's a valid img URL
            $('#image').addClass('is-invalid');
            isValid = false;
        }

        // Validate Summary
        if (!$('#summary').val().trim()) {
            $('#summary').addClass('is-invalid');
            isValid = false;
        }

        // Validate Actors
        if (!$('#actors').val().trim()) {
            $('#actors').addClass('is-invalid');
            isValid = false;
        }

        // Validate Genres
        if (!$('#genres').val().trim()) {
            $('#genres').addClass('is-invalid');
            isValid = false;
        }

        if (isValid) {
            // Proceed with AJAX request to submit form data
            $.ajax({
                url: '/add', // Update this URL to your server endpoint
                type: 'POST',
                data: $(this).serialize(), // the form input becomes a text string
                success: function(response) {
                    // Assuming the server response includes the new item's ID or details for viewing
                    var newItemId = response.id; // Update according to your actual response structure

                    // Display success message and view link
                    $('#addKdramaForm').before('<div class="success-message alert alert-success" role="alert">New item successfully created. <a href="/view/' + newItemId + '">See it here</a></div>');

                    // Clear form fields
                    $('#addKdramaForm').trigger('reset');

                    // Set focus to the first input field
                    $('#addKdramaForm input:first').focus();
                },
                error: function(xhr, status, error) {
                    // Handle submission error (e.g., display a general error message)
                    $('#addKdramaForm').before('<div class="alert alert-danger" role="alert">An error occurred. Please try again later.</div>');
                }
            });
        } else {
            console.log('Validation failed, user must correct the form');
        }
        

    });

    // Optionally, you can provide real-time validation as the user types or corrects the entries
    /*
    $('.form-control').on('input', function() {
        if ($(this).val().trim()) {
            $(this).removeClass('is-invalid');
        }
    });
    */

});
