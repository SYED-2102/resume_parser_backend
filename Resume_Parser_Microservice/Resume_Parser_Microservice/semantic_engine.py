from sentence_transformers import SentenceTransformer,util
#1 load the pretrained BERT model
#'all-MiniLM-L6-v2' is a lightweight model perfect for semantic similarity on standard hardware
#We load it globally so your server doesn't crash reloading it for every single candidate
print("INITIALIZING BERT MODEL: Downloading/Loading weights into RAM...")
model=SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(extracted_skills,job_description_text):
    """
    converts text to high-dimensional vectors and calculates cosine similarity
    """
    if not extracted_skills:
        return 0.0
    
    # We join the AI-extracted skills into a single string for the math model
    resume_text = " ".join(extracted_skills)

    # 2. Vectorization: Converting human text into mathematical embeddings
    resume_vector = model.encode(resume_text)
    job_vector = model.encode(job_description_text)

    # 3. Calculate Cosine Similarity
    # util.cos_sim returns a PyTorch tensor. We use .item() to extract the raw float value.
    similarity_tensor = util.cos_sim(resume_vector, job_vector)
    raw_score = similarity_tensor.item()

    # 4. Format into a percentage
    match_percentage = round(raw_score * 100, 2)
    
    return match_percentage