function addDimension() {
    console.log("Adding a new dimension...");

    // Allow for new dimension only if the "Add dimension" button is not disabled.
    if(document.getElementById("addDimensionsButtonId").getAttribute("disabled") == null) {

        // Allow for new dimension only if the max dimensions limit (6) will not be exceeded.
        var numOfDimensions = $("#dimensionsContainerId").children().length;
        if(numOfDimensions < 6) {

            // For unique dimension id, convert random number to base 36 and pick the first 9 characters following decimal.
            var id = '_' + Math.random().toString(36).substr(2, 9);
            console.log("New dimension id: dimensionContainerId", (id + 1));

            var newDimension = "\n" +
                "        <div class=\"container-fluid form-group has-warning has-feedback dimension-bar\" id=\"dimensionContainerId" + (id + 1) + "\">\n" +
                "            <!-- Search form -->\n" +
                "            <div class=\"dimension-form input-group-sm mb-3\">\n" +
                "                <!--<label for=\"dimension1\">Enter search terms... Tab for each term.</label>-->\n" +
                "                <input class=\"form-control\" id=\"dimension" + (id + 1) + "\" type=\"text\" data-role=\"tagsinput\" placeholder=\"Enter search terms... Tab after each term.\" aria-label=\"Search\">\n" +
                "            </div>\n" +
                "            <div class=\"remove-dimension-button\">\n" +
                "                <!-- Remove dimension button -->\n" +
                "                <div class=\"text-center\">\n" +
                "                    <a class=\"btn btn-default btn-sm\" id=\"removeDimension" + (id + 1) + "Id\" onclick=\"removeDimension(dimensionContainerId" + (id + 1) + ")\">\n" +
                "                        <span class=\"glyphicon glyphicon-minus\"></span> Remove dimension\n" +
                "                    </a>\n" +
                "                </div>\n" +
                "                <label hidden class=\"control-label max-words-warning\" id=\"warningLabelId" + (id + 1) + "\" for=\"dimension" + (id + 1) + "\">Maximum 3 words per search term.</label>\n" +
                "            </div>";
                "        </div>";
            $("#dimensionsContainerId").append(newDimension);

            // Set the maxiumum number of search terms within a dimension.
            // Also set the maximum number of characters within a search term as well.
            $('input[id^="dimension"]').tagsinput({
                maxTags: 6,  // Maximum number of search terms within a dimension.
                maxChars: 100    // Maximum number of characters within a search term.
            });

            // Set the maximum number of words within a search term.
            $('input[id^="dimension"]').bind('beforeItemAdd', function(event) {
                var searchTerm = event.item;    // search term
                if(searchTerm.split(' ').length > 3) {
                    console.log("Search terms should contain a maximum of 3 words.");
                    event.cancel = true;    // set to true in order to prevent the item from getting added
                    var id = $(this).attr("id").split('_')[1];
                    console.log("id: ", id);
                    document.getElementById("warningLabelId_" + id).removeAttribute("hidden");
                }
                else
                {
                    var id = $(this).attr("id").split('_')[1];
                    console.log("id: ", id);
                    document.getElementById("warningLabelId_" + id).setAttribute("hidden", "hidden");
                }
            });

            // Disable "Add dimension" button when the number of dimensions reach 6.
            if (numOfDimensions + 1 == 6) {
                console.log("max");
                document.getElementById("addDimensionsButtonId").setAttribute("disabled", "disabled");
            }

        } else {
            console.log("Maximum number of dimensions is 6.");
        }
    } else {
        console.log("Adding dimension is disabled.");
    }
}

function removeDimension(dimensionId) {
    console.log("Removing dimension: ", dimensionId , "...");
    $(dimensionId).remove();

    // Enable "Add dimension" button.
    document.getElementById("addDimensionsButtonId").removeAttribute("disabled");
}
