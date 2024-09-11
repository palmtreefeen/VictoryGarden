let map;
let heatmap;
let climateHeatmap;

function initMap() {
    console.log('Initializing map...');
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.7128, lng: -74.0060 }, // New York City
        zoom: 13,
    });
    console.log('Map initialized');

    // Fetch produce data from the server
    console.log('Fetching produce data...');
    fetch('/api/produce_data')
        .then(response => response.json())
        .then(data => {
            console.log('Produce data received:', data);
            addMarkers(data);
            addProduceHeatMap(data);
            console.log('Produce heatmap initialized:', heatmap);
        })
        .catch(error => console.error('Error fetching produce data:', error));

    // Add climate and planting zones heat map
    addClimateHeatMap();
}

function addMarkers(locations) {
    console.log('Adding markers...');
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
    console.log('Markers added');
}

function addProduceHeatMap(locations) {
    console.log('Adding produce heatmap...');
    const heatmapData = locations.map(location => ({
        location: new google.maps.LatLng(location.lat, location.lng),
        weight: location.organic ? 0.8 : 0.5, // Higher weight for organic produce
    }));

    heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: map,
    });
    console.log('Produce heatmap added');
}

function toggleProduceHeatmap() {
    console.log('Toggling produce heatmap...');
    if (heatmap) {
        console.log('Heatmap exists');
        const currentMap = heatmap.getMap();
        console.log('Current map:', currentMap ? 'visible' : 'hidden');
        heatmap.setMap(currentMap ? null : map);
        console.log('Heatmap visibility toggled:', currentMap ? 'hidden' : 'visible');
    } else {
        console.error('Heatmap not initialized');
    }
}

function changeRadius() {
    const currentRadius = heatmap.get("radius");
    const newRadius = currentRadius ? null : 20;
    heatmap.set("radius", newRadius);
    console.log('Heatmap radius changed to:', newRadius);
}

function changeGradient() {
    const currentGradient = heatmap.get("gradient");
    const newGradient = currentGradient ? null : [
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
    heatmap.set("gradient", newGradient);
    console.log('Heatmap gradient changed:', newGradient ? 'custom gradient' : 'default gradient');
}

function addClimateHeatMap() {
    console.log('Adding climate zone heatmap...');
    fetch('/api/climate_zones')
        .then(response => response.json())
        .then(data => {
            console.log('Climate zone data received:', data);
            const climateHeatmapData = data.map(zone => ({
                location: new google.maps.LatLng(zone.lat, zone.lng),
                weight: zone.weight
            }));

            climateHeatmap = new google.maps.visualization.HeatmapLayer({
                data: climateHeatmapData,
                map: null, // Initially not displayed
                gradient: getClimateGradient()
            });
            console.log('Climate zone heatmap initialized:', climateHeatmap);
        })
        .catch(error => console.error('Error fetching climate zone data:', error));
}

function getClimateGradient() {
    return [
        'rgba(0, 255, 0, 0)',   // Transparent green
        'rgba(0, 255, 0, 1)',   // Solid green
        'rgba(255, 255, 0, 1)', // Yellow
        'rgba(255, 128, 0, 1)', // Orange
        'rgba(255, 0, 0, 1)'    // Red
    ];
}

function toggleClimateHeatmap() {
    console.log('Toggling climate zone heatmap...');
    if (climateHeatmap) {
        console.log('Climate heatmap exists');
        const currentMap = climateHeatmap.getMap();
        console.log('Current map:', currentMap ? 'visible' : 'hidden');
        climateHeatmap.setMap(currentMap ? null : map);
        console.log('Climate heatmap visibility toggled:', currentMap ? 'hidden' : 'visible');
    } else {
        console.error('Climate heatmap not initialized');
    }
}

// Initialize the map when the page loads
window.onload = initMap;

console.log('map.js loaded');
