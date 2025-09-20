/**
 * Dispatches a task to a specific driver by sending a request to the backend server.
 * The backend is responsible for all validation.
 * @param {string} driverId - The ID of the driver to dispatch the task to.
 * @param {object} taskData - The task data, including the secure_token for authentication.
 */
function dispatchTask(driverId, taskData) {
    const webhookUrl = `http://localhost:5000/driver/${driverId}`;

    fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
    })
    .then(response => {
        if (!response.ok) {
            // Log the error response from the server for better debugging
            return response.json().then(err => { throw new Error(err.message || `Server responded with ${response.status}`) });
        }
        return response.json();
    })
    .then(data => {
        console.log('Dispatch successful:', data);
        // These functions would be defined elsewhere in a real application
        notifyTelegram(data.driver, '任務已派送！ (Server-side validation)');
        integrateUber(taskData);
    })
    .catch(error => {
        console.error('Dispatch failed:', error);
    });
}

/**
 * Sends a notification message to a user via the Telegram Bot API.
 * NOTE: This is a client-side implementation, which is insecure as it exposes the BOT_TOKEN.
 * In a real application, this should be handled by the backend.
 * @param {string} driverId - The chat_id of the Telegram user.
 * @param {string} message - The message to send.
 */
function notifyTelegram(driverId, message) {
    // This requires process.env.BOT_TOKEN, which is not available in browser environments.
    // This code is for demonstration in a Node.js environment.
    if (typeof process === 'undefined' || !process.env.BOT_TOKEN) {
        console.log(`Telegram Notification to ${driverId}: ${message}`);
        return;
    }
    fetch(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: driverId, text: message })
    });
}

/**
 * Integrates with the Uber API to request a ride.
 * NOTE: This is a client-side implementation, which is insecure as it exposes the API_KEY.
 * In a real application, this should be handled by the backend.
 * @param {object} taskData - Data containing pickup and dropoff locations.
 */
function integrateUber(taskData) {
    // This requires process.env.UBER_API_KEY, which is not available in browser environments.
    // This code is for demonstration in a Node.js environment.
    if (typeof process === 'undefined' || !process.env.UBER_API_KEY) {
        console.log(`Uber Integration: Ride requested for task.`);
        return;
    }
    fetch('https://api.uber.com/v1.2/requests', {
        method: 'POST',
        headers: {
            'Authorization': `Token ${process.env.UBER_API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: 'a1111c8c-c720-46c3-8538-2fcdd730040d', // Example Product ID
            fare_id: null,
            upfront_fare_id: null,
            pickup: { latitude: 24.1477, longitude: 120.6736 }, // Example: Taichung
            dropoff: {
                latitude: taskData.location.lat || 24.1477,
                longitude: taskData.location.lng || 120.6736
            }
        })
    }).then(res => res.json()).then(uberData => console.log('Uber dispatch response:', uberData));
}

// --- Sample Usage ---
const sampleTask = {
    type: "delivery",
    location: { lat: 24.1477, lng: 120.6736, name: "Taichung Station (臺中站)" },
    reward: 120,
    deadline: "2025-08-26T23:59:59Z",
    // Using a valid TrueCode from the unified dataset
    secure_token: "AURORA-774X-VT39-LM09",
    language: "zh-TW",
    channel: "Telegram/Uber"
};

// To run this script, you would need a Node.js environment with .env file for environment variables.
// Example: dispatchTask("driver-001", sampleTask);
console.log("dispatcher.js loaded. Call dispatchTask() with a driver ID and task data to test.");
