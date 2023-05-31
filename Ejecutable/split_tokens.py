import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

def break_up_file(tokens, chunk_size, overlap_size):
    if len(tokens) <= chunk_size:
        yield tokens
    else:
        chunk = tokens[:chunk_size]
        yield chunk
        yield from break_up_file(tokens[chunk_size-overlap_size:], chunk_size, overlap_size)

def break_up_file_to_chunks(text, chunk_size=2000, overlap_size=100):
    tokens = word_tokenize(text)
    return list(break_up_file(tokens, chunk_size, overlap_size))

def count_tokens(text):
    tokens = word_tokenize(text)
    return len(tokens)