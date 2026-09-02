import numpy as np
from collections import Counter

class TFIDFVectorizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.idf = None
        self.is_fit = False
        
    def fit(self, texts):
        if not self.tokenizer.is_fit:
            self.tokenizer.fit(texts)
            
        N = len(texts)
        vocab_size = self.tokenizer.get_vocab_size()
        
        # document frequency (df) for each token
        df = np.zeros(vocab_size)
        
        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            token_ids = set([self.tokenizer.vocab.get(token, 0) for token in tokens])
            for token_id in token_ids:
                df[token_id] += 1
                
        # idf(t) = log(N / (1 + df(t)))
        self.idf = np.log(N / (1 + df))
        self.is_fit = True
        
    def transform(self, texts):
        if not self.is_fit:
            raise ValueError("Vectorizer must be fit before calling transform.")
            
        vocab_size = self.tokenizer.get_vocab_size()
        vectors = []
        
        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            doc_len = len(tokens)
            
            # tf(t, d) = count(t in d) / len(d)
            token_ids = [self.tokenizer.vocab.get(token, 0) for token in tokens]
            counts = Counter(token_ids)
            
            vector = np.zeros(vocab_size)
            if doc_len > 0:
                for token_id, count in counts.items():
                    tf = count / doc_len
                    vector[token_id] = tf * self.idf[token_id]
            vectors.append(vector)
            
        return np.array(vectors)
