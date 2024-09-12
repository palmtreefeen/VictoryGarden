document.addEventListener('DOMContentLoaded', function() {
    const gardenGrid = document.getElementById('garden-grid');
    const plantList = document.getElementById('plant-list');
    const gridSize = 10;

    // Create garden grid
    for (let i = 0; i < gridSize * gridSize; i++) {
        const cell = document.createElement('div');
        cell.classList.add('garden-cell');
        cell.addEventListener('click', function() {
            const selectedPlant = document.querySelector('.plant-item.selected');
            if (selectedPlant) {
                cell.style.backgroundColor = selectedPlant.dataset.color;
                cell.textContent = selectedPlant.textContent;
            }
        });
        gardenGrid.appendChild(cell);
    }

    // Create plant palette
    const plants = [
        { name: 'Tomato', color: '#ff6347' },
        { name: 'Lettuce', color: '#90ee90' },
        { name: 'Carrot', color: '#ffa500' },
        { name: 'Pepper', color: '#ff4500' },
        { name: 'Cucumber', color: '#32cd32' }
    ];

    plants.forEach(plant => {
        const listItem = document.createElement('li');
        listItem.classList.add('plant-item');
        listItem.textContent = plant.name;
        listItem.dataset.color = plant.color;
        listItem.style.backgroundColor = plant.color;
        listItem.addEventListener('click', function() {
            document.querySelectorAll('.plant-item').forEach(item => item.classList.remove('selected'));
            this.classList.add('selected');
        });
        plantList.appendChild(listItem);
    });

    // Companion planting functionality
    const companionPlanting = {
        'Tomato': {
            good: ['Basil', 'Carrots', 'Onions'],
            bad: ['Potatoes', 'Cabbage', 'Fennel']
        },
        'Lettuce': {
            good: ['Carrots', 'Radishes', 'Cucumbers'],
            bad: ['Broccoli', 'Celery']
        },
        'Carrot': {
            good: ['Tomatoes', 'Onions', 'Peas'],
            bad: ['Dill', 'Parsnips']
        },
        'Pepper': {
            good: ['Onions', 'Carrots', 'Spinach'],
            bad: ['Beans', 'Kale']
        },
        'Cucumber': {
            good: ['Beans', 'Peas', 'Radishes'],
            bad: ['Potatoes', 'Aromatic Herbs']
        }
    };

    const plantSelector = document.getElementById('plant-selector');
    const goodCompanions = document.getElementById('good-companions');
    const badCompanions = document.getElementById('bad-companions');

    plantSelector.addEventListener('change', function() {
        const selectedPlant = this.value;
        const companions = companionPlanting[selectedPlant];

        goodCompanions.innerHTML = '';
        badCompanions.innerHTML = '';

        companions.good.forEach(plant => {
            const li = document.createElement('li');
            li.textContent = plant;
            goodCompanions.appendChild(li);
        });

        companions.bad.forEach(plant => {
            const li = document.createElement('li');
            li.textContent = plant;
            badCompanions.appendChild(li);
        });
    });

    // Initialize companion planting guide with the first plant
    plantSelector.dispatchEvent(new Event('change'));
});
