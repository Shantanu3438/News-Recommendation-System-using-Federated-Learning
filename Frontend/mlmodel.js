
// Define the global model's architecture
function createModel(inputShape) {
    const model = tf.sequential();
    model.add(tf.layers.dense({ units: 52, activation: 'relu', inputShape: inputShape }));
    model.add(tf.layers.dense({ units: 32, activation: 'relu' }));
    model.add(tf.layers.dense({ units: 1, activation: 'sigmoid' }));
    return model;
}

// Create the model
const model = createModel([52]);

// Compile the model
model.compile({
    optimizer: 'adam',
    loss: 'binaryCrossentropy',
    metrics: ['accuracy']
});

// Train the model
async function trainModel(inputData) {
    const user_id = parseInt(inputData.user_id);
    const interaction_data = tf.tensor(inputData.interaction_data);
    const feature_vector = tf.tensor(inputData.feature_vector);
    const user_id_tensor = tf.tensor([user_id]);

    // Concatenate user_id, interaction_data, and feature_vector
    let concatenated_tensor = tf.concat([user_id_tensor, interaction_data, feature_vector], 0);
    concatenated_tensor = tf.reshape(concatenated_tensor, [1, 52])
    const history = await model.fit(concatenated_tensor, interaction_data, {
        epochs: 1,
        batchSize: 1
    });
    return history;
}

async function initializeModel() {
    try {
        const response = await fetch('http://localhost:8000/global-weights/');
        if (!response.ok) {
            throw new Error('Failed to fetch global weights');
        }
        const data = await response.json();
        const globalWeightsData = JSON.parse(data);
        const globalWeight = [];
        for (let i = 0; i < globalWeightsData.length; i++) {
            const subArray = globalWeightsData[i];
            const tensor = tf.tensor(subArray);
            globalWeight.push(tensor)
        }
        await model.setWeights(globalWeight);
        console.log("Model initialized !");
    } catch (error) {
        console.log("Error initializing local model:", error);
    }
}


async function updateGlobalModel() {
    let localWeight = model.getWeights();
    const finalWeight = [];
    await Promise.all(localWeight.map(async (subArray) => {
        const data = await subArray.data();
        finalWeight.push(data);
    }));
    
    const response = await fetch(
        'http://localhost:8000/update-global-model/',
        {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(finalWeight),
        }
        );
        
        if (!response.ok) {
            throw new Error('Could not update global model');
        } else {
            console.log('Global model updated !');
        }
    }
    
    
    initializeModel();

// Train the model
// trainModel().then((history) => {
//     console.log('Training completed.');
//     // Get the trained weights
//     const weights = model.getWeights();
//     console.log('Trained weights:', weights);
// }).catch((error) => {
//     console.error('Error during training:', error);
// });