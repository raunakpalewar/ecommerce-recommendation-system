const BASE_URL = 'http://127.0.0.1:8000/';

function fetchData(apiEndpoint, elementId, key) {
    fetch(BASE_URL + apiEndpoint)
        .then(response => response.json())
        .then(data => {
            const dropdown = document.getElementById(elementId);

            // Clear existing options
            dropdown.innerHTML = '';

         
            if (elementId !== 'rating') {
            // Add a default "Select" option
            const defaultOption = document.createElement("option");
            defaultOption.value = 'Select';  // You can set value to empty or some default value
            defaultOption.text = "Select";  // Display "Select" as the default option
            dropdown.add(defaultOption);
            }
            // Populate dropdown with data
            data[key].forEach(item => {
                const option = document.createElement("option");
                option.value = item;  // Set the value for the option
                option.text = item;
                dropdown.add(option);
            });
        })
        .catch(error => console.error('Error:', error));
}


// Fetch data for brands
fetchData('AllBrands/', 'brand', 'brands');

// Fetch data for categories
fetchData('AllCategories/', 'category', 'categories');

// Fetch data for subcategories
fetchData('AllSubcategories/', 'subcategory', 'subcategories');

// Fetch data for ratings
fetchData('AverageRating/', 'rating', 'average_rating');

// Fetch data for price range
fetchData('PriceRange/', 'price', 'price_range');

window.addEventListener('load', (event) => {
    // Set up event listener for price range
    const priceRange = document.getElementById('price');
    const priceValueSpan = document.getElementById('priceValue');
    const minPriceSpan = document.getElementById('minPrice');
    const maxPriceSpan = document.getElementById('maxPrice');

    

    priceRange.addEventListener('input', () => {
        const priceValue = priceRange.value;
        priceValueSpan.innerText = priceValue; // Update displayed price value
        // Do something with the selected price value
    });

  
    
    
    fetch(BASE_URL + 'PriceRange/')
        .then(response => response.json())
        .then(data => {
            console.log('Price Range API Response:', data);
            const minPrice = data.min_price;
            const maxPrice = data.max_price;
            console.log('Min Price:', minPrice, 'Max Price:', maxPrice);
            minPriceSpan.innerText = minPrice;
            maxPriceSpan.innerText = maxPrice;
        })
        .catch(error => console.error('Error:', error));
});