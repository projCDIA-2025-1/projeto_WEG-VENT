import ollama

def summarize_with_ollama(abstract, full_text, model="qwen2.5:7b"):
    """
    Generate a summary of chemical reaction text using Ollama
    Args:
    text (str): The text to summarize
    model (str): Ollama model to use (qwen2.5:7b handles long contexts well)
    Returns:
    str: Generated summary or error message
    """
    text =  full_text if full_text is not None else abstract
    prompt = f"""Please provide a concise scientific resume of this chemical reaction report. Focus on:
        1. The usage of this patent in the context of chemical reactions
        2. Any notable observations or results
        I want a small resume to know the main points of this chemical reaction report. Just answer with the context of the text, do not include any other conclusion. Follow this steps:
        ***Process***:
        ***Method***
        (Any notable observation, if interesting as ***Insight***)
        ***Outcome***:
        Text to resume:
        {text}

        Summary:"""

    try:
        response = ollama.generate(
        model=model,
        prompt=prompt,
        options={
        "temperature": 0.3, # Lower temperature for more focused summaries
        "top_p": 0.9,
        "num_ctx": 8192 # Context window size - adjust based on your model
        }
        )
        return response['response']
    except Exception as e:
        return f"Error generating summary: {str(e)}"

if __name__ == "__main__":
# sample_dir = "./chemu_sample/ner"
# process_directory(sample_dir)
    text = """
    Provided is a method of producing isolated graphene sheets directly from a carbon/graphite precursor. The method comprises: (a) providing a mass of aromatic molecules wherein the aromatic molecules are selected from petroleum heavy oil or pitch, coal tar pitch, a polynuclear hydrocarbon, or a combination thereof; (b) heat treating this mass and using chemical or mechanical means to form graphene domains dispersed in a disordered matrix of carbon or hydrocarbon molecules, wherein the graphene domains are each composed of from 1 to 30 planes of hexagonal carbon atoms or fused aromatic rings having a length or width from 5 nm to 20 Î¼m and an inter-graphene space between two planes of hexagonal carbon atoms or fused aromatic rings no less than 0.4 nm; and (c) separating and isolating the planes of hexagonal carbon atoms or fused aromatic rings to recover graphene sheets from the disordered matrix.
    
    """
    print("entering in the ollama summarization function")
    output = summarize_with_ollama(text,"", model="qwen2.5:7b")
    print("Summary Output:")
    print(output)
