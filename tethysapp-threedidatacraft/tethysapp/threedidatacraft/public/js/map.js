$(function () {
    // Create new Overlay with the #popup element
    var popup = new ol.Overlay({
        element: document.getElementById('popup')
    });

    // Get the Open Layers map object from the Tethys MapView
    var map = TETHYS_MAP_VIEW.getMap();

    // Get the Select Interaction from the Tethys MapView
    var select_interaction = TETHYS_MAP_VIEW.getSelectInteraction();

    // Add the popup overlay to the map
    map.addOverlay(popup);

    // When selected, call function to display properties
    select_interaction.getFeatures().on('change:length', function (e) {
        var popup_element = popup.getElement();

        if (e.target.getArray().length > 0) {
            // this means there is at least 1 feature selected
            var selected_feature = e.target.item(0); // 1st feature in Collection

            // Get coordinates of the point to set position of the popup
            var coordinates = selected_feature.getGeometry().getCoordinates();
            console.log(selected_feature)

            var popup_content = 
                '<a href="#" id="popup-closer" class="ol-popup-closer"></a>' +
                '<div class="station-popup">' +
                '<div class="popup-content">' +
                '<h5>ID: ' + selected_feature.get('id') + '</h5>' +
                '<h6>Location:</h6>' +
                '<span>' + coordinates[0] + ', ' + coordinates[1] + '</span>' +
                '<h6>Waterlevel <a href="'+'/apps/threedidatacraft/benchmark/' + selected_feature.get('id') + '" class="">Benchmark</a>' + '</h6>' +
                '<div id="plot-content"></div>' +
                '</div>' +
                '</div>';

            // Clean up last popup and reinitialize
            $(popup_element).popover('dispose');

            // Delay arbitrarily to wait for previous popover to
            // be deleted before showing new popover.
            setTimeout(function () {
                popup.setPosition(coordinates);
                popup_element.innerHTML = popup_content;
                $(popup_element).popover('show');
                $('#plot-content').load('/apps/threedidatacraft/plot/' + selected_feature.get('id') + '/ajax/');

                const closer = document.getElementById('popup-closer');
                // const download = document.getElementById('popup-export');
                closer.onclick = function () {
                    popup.setPosition(undefined);
                    closer.blur();
                    return false;
                };
                // download.onclick = function () {
                //     alert('Comming soon')
                //     return false;
                // };
            }, 500);

        } else {
            // remove pop up when selecting nothing on the map
            $(popup_element).popover('dispose');
        }
    });
});