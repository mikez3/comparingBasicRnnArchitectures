# -*- coding: utf-8 -*-
"""ComparingBasicRNNArchitectures.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bbt3yi8XmgIcWf-AGFIZlYpVSDZhFkSl
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, SimpleRNN
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from google.colab import drive

# Load data
drive.mount('/content/gdrive')
agg_data = np.loadtxt('/content/gdrive/My Drive/2h_ergasia_NN/data/CoffeeMachinemaxAgg.txt', delimiter=',')
app_data = np.loadtxt('/content/gdrive/My Drive/2h_ergasia_NN/data/CoffeeMachinemaxApp.txt', delimiter=',')
input_data = np.loadtxt('/content/gdrive/My Drive/2h_ergasia_NN/data/Input_Data.txt', delimiter=',')
output_data = np.loadtxt('/content/gdrive/My Drive/2h_ergasia_NN/data/Output_Data.txt', delimiter=',')
# Normalize data
agg_max = np.max(agg_data)
app_max = np.max(app_data)
input_data_normalized = input_data / agg_max
output_data_normalized = output_data / app_max

# Split data into training and testing sets
train_ratio = 0.8
num_samples = input_data.shape[0]
seq_length = input_data.shape[1]
train_size = int(train_ratio * num_samples)

X_train = input_data_normalized[:train_size].reshape((train_size, seq_length, 1))
X_test = input_data_normalized[train_size:].reshape((num_samples - train_size, seq_length, 1))
y_train = output_data_normalized[:train_size].reshape((train_size, seq_length, 1))
y_test = output_data_normalized[train_size:].reshape((num_samples - train_size, seq_length, 1))

# Plot random samples from test set
def plot_random_samples(X_test, y_test, num_samples=3):

  for _ in range (num_samples):
    idx = np.random.randint(len(X_test))
    # Create a figure and axis
    fig, ax1 = plt.subplots()
    # Create a second y-axis
    ax2 = ax1.twinx()
    # Plot the first array on the primary y-axis
    ax1.plot(X_test[idx], label='Total Consumption', color='dodgerblue', linewidth=4)
    # Plot the first array on the secondary y-axis
    ax2.plot(y_test[idx], label='Coffee Machine Consumption', color='r')
    ax1.set_ylabel('aggregated signal (W)', color = 'dodgerblue')
    ax2.set_ylabel('appliance signal (W)', color = 'r')
    ax1.tick_params(axis='y', labelcolor='dodgerblue')
    ax2.tick_params(axis='y', labelcolor='r')
    plt.grid(True)
    ax1.set_xlabel('Time (minutes)')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
plot_random_samples(input_data, output_data)

# Define model architecture
def create_model(model_type, input_shape):
    model = Sequential()
    if model_type == 'LSTM':
        model.add(LSTM(4, input_shape=input_shape, return_sequences=True))
    elif model_type == 'GRU':
        model.add(GRU(4, input_shape=input_shape, return_sequences=True))
    else:
        model.add(SimpleRNN(4, input_shape=input_shape, return_sequences=True))
    model.add(Dense(1, activation="linear"))
    model.compile(optimizer=Adam(learning_rate= 0.0001), loss=MeanSquaredError())
    return model

input_shape = (seq_length, 1)

model_lstm = create_model('LSTM', input_shape)
model_rnn = create_model('RNN', input_shape)
model_gru = create_model('GRU', input_shape)

# Train the models
epochs = 50

history_lstm = model_lstm.fit(X_train, y_train, epochs=epochs, validation_split=0.2, callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)], batch_size=32)
history_rnn = model_rnn.fit(X_train, y_train, epochs=epochs, validation_split=0.2, callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)], batch_size=32)
history_gru = model_gru.fit(X_train, y_train, epochs=epochs, validation_split=0.2, callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)], batch_size=32)

# Plot training history
def plot_history(history, title):
    plt.figure(figsize=(14, 6))
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title(title)
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.show()

plot_history(history_lstm, 'LSTM Model Loss')
plot_history(history_rnn, 'RNN Model Loss')
plot_history(history_gru, 'GRU Model Loss')

# Evaluate models and store predictions
def evaluate_model(model, X_test, y_test, app_max):
    predictions = model.predict(X_test)
    predictions_denorm = predictions * app_max
    y_test_denorm = y_test * app_max
    # Calculate errors for each sequence in the test set
    rmse_per_seq = [mean_squared_error(y_test_denorm[i].flatten(), predictions_denorm[i].flatten()) for i in range(len(y_test))]
    mae_per_seq = [mean_absolute_error(y_test_denorm[i].flatten(), predictions_denorm[i].flatten()) for i in range(len(y_test))]
    max_error_per_seq = [np.max(np.abs(y_test_denorm[i].flatten() - predictions_denorm[i].flatten())) for i in range(len(y_test))]
    # Calculate errors in total
    rmse = np.sqrt(mean_squared_error(y_test_denorm.flatten(), predictions_denorm.flatten()))
    mae = mean_absolute_error(y_test_denorm.flatten(), predictions_denorm.flatten())
    max_error = np.max(np.abs(y_test_denorm.flatten() - predictions_denorm.flatten()))
    return rmse, mae, max_error, rmse_per_seq, mae_per_seq, max_error_per_seq,  predictions

rmse_lstm, mae_lstm, max_error_lstm, rmse_per_seq_lstm, mae_per_seq_lstm, max_error_per_seq_lstm, predictions_lstm = evaluate_model(model_lstm, X_test, y_test, app_max)
rmse_rnn, mae_rnn, max_error_rnn, rmse_per_seq_rnn, mae_per_seq_rnn, max_error_per_seq_rnn, predictions_rnn = evaluate_model(model_rnn, X_test, y_test, app_max)
rmse_gru, mae_gru, max_error_gru, rmse_per_seq_gru, mae_per_seq_gru, max_error_per_seq_gru, predictions_gru = evaluate_model(model_gru, X_test, y_test, app_max)

print(f"LSTM RMSE: {rmse_lstm}, MAE: {mae_lstm}, Max Error: {max_error_lstm}")
print(f"RNN RMSE: {rmse_rnn}, MAE: {mae_rnn}, Max Error: {max_error_rnn}")
print(f"GRU RMSE: {rmse_gru}, MAE: {mae_gru}, Max Error: {max_error_gru}")

# Plot RMSE per sequence for each model
plt.figure(figsize=(12, 6))
plt.plot(rmse_per_seq_lstm, label='LSTM', marker='o', linestyle='-', color='dodgerblue',markersize=9, linewidth=6)
plt.plot(rmse_per_seq_rnn, label='RNN', marker='s', linestyle='-', color='darkorange', linewidth=3)
plt.plot(rmse_per_seq_gru, label='GRU', marker='x', linestyle='--', color='darkgreen')
plt.title('RMSE per Sequence for Different Models')
plt.xlabel('Sequence Index')
plt.ylabel('RMSE')
plt.legend()
plt.grid(axis='y')
plt.show()
# Plot MAE per sequence for each model
plt.figure(figsize=(12, 6))
plt.plot(mae_per_seq_lstm, label='LSTM', marker='o', linestyle='-', color='dodgerblue',markersize=9, linewidth=6)
plt.plot(mae_per_seq_rnn, label='RNN', marker='s', linestyle='-', color='darkorange', linewidth=3)
plt.plot(mae_per_seq_gru, label='GRU', marker='x', linestyle='--', color='darkgreen')
plt.title('MAE per Sequence for Different Models')
plt.xlabel('Sequence Index')
plt.ylabel('MAE')
plt.legend()
plt.grid(axis='y')
plt.show()
# Plot max error per sequence for each model
plt.figure(figsize=(12, 6))
plt.plot(max_error_per_seq_lstm, label='LSTM', marker='o', color='dodgerblue',markersize=9, linewidth=6)
plt.plot(max_error_per_seq_rnn, label='RNN', marker='s', color='darkorange', linewidth=3)
plt.plot(max_error_per_seq_gru, label='GRU', marker='x', linestyle='--', color='darkgreen')
plt.title('Max Error per Sequence for Different Models')
plt.xlabel('Sequence Index')
plt.ylabel('Max Error')
plt.legend()
plt.grid(axis='y')
plt.show()

# Select specific rows from test set
active_indices = [i for i in range(len(y_test)) if np.any(y_test[i] > 0)]
inactive_indices = [i for i in range(len(y_test)) if np.all(y_test[i] == 0)]

def plot_specific_samples(X_test, y_test, predictions_lstm, predictions_rnn, predictions_gru, indices):
    for idx in indices:
        plt.figure(figsize=(10, 5))
        plt.plot(y_test[idx].flatten() * app_max, label='Actual Coffee Machine Consumption', color='b')
        plt.plot(predictions_lstm[idx].flatten() * app_max, label='Predicted Coffee Machine Consumption (LSTM)', color='r')
        plt.plot(predictions_rnn[idx].flatten() * app_max, label='Predicted Coffee Machine Consumption (RNN)', color='g')
        plt.plot(predictions_gru[idx].flatten() * app_max, label='Predicted Coffee Machine Consumption (GRU)', color='y')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Power Consumption (W)')
        plt.legend()
        plt.show()

# Plot active and inactive samples
plot_specific_samples(X_test, y_test, predictions_lstm, predictions_rnn, predictions_gru, active_indices[:2])
plot_specific_samples(X_test, y_test, predictions_lstm, predictions_rnn, predictions_gru, inactive_indices[:2])