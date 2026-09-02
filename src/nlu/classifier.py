import numpy as np
import json
import os

class IntentClassifier:
    def __init__(self, input_size, num_classes, hidden_size=128):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_classes = num_classes
        
        # Xavier/Glorot initialization for weights
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / (input_size + hidden_size))
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, num_classes) * np.sqrt(2.0 / (hidden_size + num_classes))
        self.b2 = np.zeros((1, num_classes))
        
        # Velocities for momentum
        self.v_W1 = np.zeros_like(self.W1)
        self.v_b1 = np.zeros_like(self.b1)
        self.v_W2 = np.zeros_like(self.W2)
        self.v_b2 = np.zeros_like(self.b2)
        
    def _relu(self, z):
        return np.maximum(0, z)
        
    def _relu_deriv(self, z):
        return (z > 0).astype(float)
        
    def _softmax(self, z):
        # Subtract max for numerical stability
        exp_scores = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        
    def forward(self, X):
        # Store values for backprop
        self.X = X
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self._relu(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.probs = self._softmax(self.z2)
        return self.probs
        
    def compute_loss(self, probs, y_true_one_hot):
        num_examples = probs.shape[0]
        # Prevent log(0)
        corect_logprobs = -np.log(probs[range(num_examples), np.argmax(y_true_one_hot, axis=1)] + 1e-10)
        data_loss = np.sum(corect_logprobs) / num_examples
        return data_loss
        
    def backward(self, y_true_one_hot):
        num_examples = self.X.shape[0]
        
        # Derivative of cross entropy with softmax
        dz2 = self.probs - y_true_one_hot
        dz2 /= num_examples
        
        # Gradients for W2 and b2
        self.dW2 = np.dot(self.a1.T, dz2)
        self.db2 = np.sum(dz2, axis=0, keepdims=True)
        
        # Backprop through ReLU
        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * self._relu_deriv(self.z1)
        
        # Gradients for W1 and b1
        self.dW1 = np.dot(self.X.T, dz1)
        self.db1 = np.sum(dz1, axis=0, keepdims=True)
        
    def step(self, learning_rate, momentum=0.9):
        # Update velocities
        self.v_W1 = momentum * self.v_W1 - learning_rate * self.dW1
        self.v_b1 = momentum * self.v_b1 - learning_rate * self.db1
        self.v_W2 = momentum * self.v_W2 - learning_rate * self.dW2
        self.v_b2 = momentum * self.v_b2 - learning_rate * self.db2
        
        # Update weights
        self.W1 += self.v_W1
        self.b1 += self.v_b1
        self.W2 += self.v_W2
        self.b2 += self.v_b2

    def save(self, model_path, intent_map):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        np.savez(
            model_path,
            W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2,
        )
        # Save intent mapping separately
        with open(model_path + "_map.json", "w") as f:
            json.dump(intent_map, f)
            
    def load(self, model_path):
        data = np.load(model_path)
        self.W1 = data['W1']
        self.b1 = data['b1']
        self.W2 = data['W2']
        self.b2 = data['b2']
        
        with open(model_path + "_map.json", "r") as f:
            intent_map = json.load(f)
        return intent_map
