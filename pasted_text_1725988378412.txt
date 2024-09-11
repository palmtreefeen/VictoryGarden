let map;
let heatmap;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.7128, lng: -74.0060 }, // Default to New York City
        zoom: 10,
    });

    // Fetch produce data from the server
    fetch('/api/produce_data')
        .then(response => response.json())
        .then(data => {
            addMarkers(data);
            addHeatMap(data);
        });
}

function addMarkers(locations) {
    locations.forEach(location => {
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
        });

        const infoWindow = new google.maps.InfoWindow({
            content: `
                <h3>${location.name}</h3>
                <p>Price: $${location.price}</p>
                <p>Organic: ${location.organic ? 'Yes' : 'No'}</p>
            `
        });

        marker.addListener('click', () => {
            infoWindow.open(map, marker);
        });
    });
}

function addHeatMap(locations) {
    const heatmapData = locations.map(location => ({
        location: new google.maps.LatLng(location.lat, location.lng),
        weight: location.organic ? 0.8 : 0.5, // Higher weight for organic produce
    }));

    heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: map,
    });
}

// Toggle heatmap visibility
function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}

// Change heatmap radius
function changeRadius() {
    heatmap.set("radius", heatmap.get("radius") ? null : 20);
}

// Change gradient
function changeGradient() {
    const gradient = [
        "rgba(0, 255, 255, 0)",
        "rgba(0, 255, 255, 1)",
        "rgba(0, 191, 255, 1)",
        "rgba(0, 127, 255, 1)",
        "rgba(0, 63, 255, 1)",
        "rgba(0, 0, 255, 1)",
        "rgba(0, 0, 223, 1)",
        "rgba(0, 0, 191, 1)",
        "rgba(0, 0, 159, 1)",
        "rgba(0, 0, 127, 1)",
        "rgba(63, 0, 91, 1)",
        "rgba(127, 0, 63, 1)",
        "rgba(191, 0, 31, 1)",
        "rgba(255, 0, 0, 1)"
    ];
    heatmap.set("gradient", heatmap.get("gradient") ? null : gradient);
}

// Initialize the map when the page loads
window.onload = initMap;
