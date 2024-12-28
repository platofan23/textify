from transformers import MarianMTModel, MarianTokenizer

def translate(texts, model_name="Helsinki-NLP/opus-mt-en-de"):
    # Tokenizer und Model laden
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    # Eingabetexte tokenisieren
    inputs = tokenizer(texts, return_tensors="pt", padding=True)

    # Übersetzung generieren
    translated = model.generate(**inputs)
    # Aus Token wieder String machen
    outputs = tokenizer.batch_decode(translated, skip_special_tokens=True)
    return outputs

if __name__ == "__main__":
    # Beispieltexte
    text_list = [
        "Hello world!",
        "This is a test sentence.",
        "How are you doing today?"
    ]
    translations = translate(text_list, "Helsinki-NLP/opus-mt-en-de")
    for i, trans in enumerate(translations):
        print(f"Original: {text_list[i]} -> Übersetzt: {trans}")