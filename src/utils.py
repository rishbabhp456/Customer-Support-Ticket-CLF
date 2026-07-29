import tensorflow as tf
import numpy as np
import config
import json

class Text_clf:
    def __init__(self):
        self.load_model()

    def load_model(self):
        """---Load model file----"""
        self.model = tf.keras.models.load_model(config.MODEL_PATH)

        """Load Text Preprocessor properly"""
        with open(config.PREPROCESSOR, 'r', encoding='utf-8') as f:
            loaded_tokenizer_json = json.load(f)
            self.tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(loaded_tokenizer_json)
        
        """ ---- Load model Class----"""
        with open(config.MODEL_CONFIG, 'r', encoding='utf-8') as f:
            self.class_names = json.load(f)

    def preprocess_text(self, input_text):
        max_len = 100
        # Create local variables instead of using self for temporary data
        seq = self.tokenizer.texts_to_sequences([input_text])
        padded_seq = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=max_len, padding='post', truncating='post')
        return padded_seq

    def make_prediction(self, input_text):
        """Preprocess text"""
        processed_text = self.preprocess_text(input_text)

        """Predict text"""
        prediction = self.model.predict(processed_text)
        predicted_class_index = np.argmax(prediction)
        
        # JSON keys are always strings, so we convert the integer index to a string
        predicted_topic = self.class_names[predicted_class_index]

        return predicted_topic, prediction

