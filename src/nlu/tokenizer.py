import re
from collections import Counter

class Tokenizer:
    def __init__(self, max_vocab_size=3000):
        self.max_vocab_size = max_vocab_size
        self.vocab = {}
        self.inv_vocab = {}
        self.unk_token = "<UNK>"
        self.is_fit = False
        
    def _preprocess(self, text):
        # Lowercase
        text = text.lower()
        # Remove punctuation, but keep spaces
        # We can replace punctuation with space or just strip it.
        text = re.sub(r'[^\w\s]', ' ', text)
        return text
        
    def tokenize(self, text):
        text = self._preprocess(text)
        # Split on whitespace
        return text.split()
        
    def fit(self, texts):
        word_counts = Counter()
        for text in texts:
            tokens = self.tokenize(text)
            word_counts.update(tokens)
            
        # We reserve index 0 for <UNK>
        self.vocab = {self.unk_token: 0}
        
        # Sort by frequency and take top max_vocab_size - 1
        most_common = word_counts.most_common(self.max_vocab_size - 1)
        
        for idx, (word, _) in enumerate(most_common, start=1):
            self.vocab[word] = idx
            
        self.inv_vocab = {v: k for k, v in self.vocab.items()}
        self.is_fit = True
        
    def transform(self, texts):
        if not self.is_fit:
            raise ValueError("Tokenizer must be fit before calling transform.")
            
        return [[self.vocab.get(token, 0) for token in self.tokenize(text)] for text in texts]

    def get_vocab_size(self):
        return len(self.vocab)
