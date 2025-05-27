# Handles prompt selection logic

# Define the 6 predefined prompts
PREDEFINED_PROMPTS = {
    ("topic", "mcq"): """You are an expert educational content generator. Create {num_of_question} unique and creatively framed multiple-choice questions that comprehensively assess understanding of the topic: "{content}". Ensure the questions vary in style—some direct, some conceptual, and some application-based—while maintaining the specified difficulty level: {level}. {subject_instruction} {exam_instruction} {custom_instruction}. Return the output strictly in this JSON format:
{{
  "context": "Here are {num_of_question} questions on the topic: {content} with {level} difficulty.",
  "topic": "{content}",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_option": "Option A",
      "explanation": "Brief explanation of the correct answer."
    }}
  ]
}}


""",
    ("topic", "true_false"): """You are an expert test designer. Generate **{num_of_question} well-balanced and logically challenging true/false questions** about the topic: **"{content}"**, ensuring a mix of facts, misconceptions, and analytical judgments at **{level}** difficulty. {subject_instruction} {exam_instruction} {custom_instruction}

Return the output strictly in this JSON format:

```json
{{
  "context": "Here are {num_of_question} questions on the topic: {content} with {level} difficulty.",
  "topic": "{content}",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "Statement text",
      "correct_option": true,
      "explanation": "Brief reasoning behind the true or false answer."
    }}
  ]
}}
```

""",

    ("topic", "fill_in_the_blanks"): """You are a creative academic assistant. Create **{num_of_question} thought-provoking fill-in-the-blank questions** on the topic: **"{content}"**, using intelligent omissions that assess conceptual understanding. Maintain a consistent tone and ensure a suitable difficulty level: {level}. {subject_instruction} {exam_instruction} {custom_instruction}

Use **underscores (___)** to indicate blanks. Return the output strictly in this JSON format:

```json
{{
  "context": "Here are {num_of_question} questions on the topic: {content} with {level} difficulty.",
  "topic": "{content}",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "The capital of France is ___",
      "options": ["Paris", "Berlin", "Rome", "Madrid"],
      "correct_option": "Paris",
      "explanation": "Paris is the capital of France."
    }}
  ]
}}
```

""",

    ("paragraph", "mcq"): """You are a quiz master AI. Carefully analyze the following paragraph and generate **{num_of_question} insightful and well-reasoned multiple-choice questions** to evaluate comprehension, inference, and critical analysis at **{level}** difficulty:

"{content}"

Incorporate diversity in questioning styles—factual recall, implications, author intent, etc. {subject_instruction} {exam_instruction} {custom_instruction}

Return the output strictly in this JSON format:

```json
{{
  "context": "Here are {num_of_question} questions derived from the paragraph with {level} difficulty.",
  "topic": "Derived from paragraph",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "Question based on paragraph",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_option": "Option B",
      "explanation": "Explanation based on paragraph analysis."
    }}
  ]
}}
```

""",

    ("paragraph", "true_false"): """Read the following paragraph and generate **{num_of_question} well-reasoned true/false statements** that require understanding of both explicit and implicit content. The goal is to test critical reading and comprehension skills at **{level}** difficulty:

"{content}"

Ensure a balanced distribution of true and false answers. {subject_instruction} {exam_instruction} {custom_instruction}

Return the output strictly in this JSON format:

```json
{{
  "context": "Here are {num_of_question} questions derived from the paragraph with {level} difficulty.",
  "topic": "Derived from paragraph",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "Statement derived from paragraph",
      "correct_option": false,
      "explanation": "Explain why it is false."
    }}
  ]
}}
```

""",

    ("paragraph", "fill_in_the_blanks"): """From the following paragraph, craft **{num_of_question} intelligent fill-in-the-blank questions** that test key facts, concepts, or contextually significant words. Use meaningful omissions and ensure a consistent tone across all questions. Target difficulty: **{level}**.

"{content}"

{subject_instruction} {exam_instruction} {custom_instruction}

Use **___** for blanks. Return the output strictly in this JSON format:

```json
{{
  "context": "Here are {num_of_question} questions derived from the paragraph with {level} difficulty.",
  
  "topic": "Derived from paragraph",
  "exam": "{exam_instruction}",
  "level": "{level}",
  "questions": [
    {{
      "stem": "The author argues that ___ is essential.",
      "options": ["freedom", "discipline", "order", "equality"],
      "correct_option": "freedom",
      "explanation": "Explanation based on paragraph logic."
    }}
  ]
}}
```

"""
}

def select_and_customize_prompt(params: dict) -> str:
    content_type = params.get("content_type") # Corrected key
    question_type = params.get("question_type") # Corrected key
    level = params.get("level")
    content = params.get("content")
    num_of_question = params.get("num_of_question") # Corrected key
    subject = params.get("subject")
    exam = params.get("refrence exam")
    custom_instruction = params.get("custom instruction")

    print(f"Prompt selector received: content_type={content_type}, question_type={question_type}, level={level}, content={content}, num_of_question={num_of_question}") # Debug print

    # Validate mandatory parameters explicitly
    missing_params = []
    if not content_type: missing_params.append("content_type")
    if not question_type: missing_params.append("question_type")
    if not level: missing_params.append("level")
    if not content: missing_params.append("content")
    if not num_of_question: missing_params.append("num_of_question")

    if missing_params:
        print(f"Missing or falsy mandatory parameters: {', '.join(missing_params)}")
        # In a real application, you'd raise a specific error or return an error indicator
        print("Missing mandatory parameters for prompt selection")
        return ""

    # Map frontend question type names to backend dictionary keys
    question_type_mapping = {
        "multiple_choice_quiz": "mcq",
        "true_false_quiz": "true_false",
        "short_answer_quiz": "short_answer", # Assuming this key exists or should exist
        "fill_in_the_blanks_quiz": "fill_in_the_blanks",
        "matching_quiz": "matching", # Assuming this key exists or should exist
        "essay_questions": "essay_questions" # Assuming this key exists or should exist
    }

    mapped_question_type = question_type_mapping.get(question_type.lower())

    if not mapped_question_type:
        print(f"Unsupported question type received: {question_type}")
        return "" # Handle unsupported type

    prompt_key = (content_type.lower(), mapped_question_type)

    print(f"Looking up prompt key: {prompt_key}") # Debug print for prompt key

    base_prompt = PREDEFINED_PROMPTS.get(prompt_key)

    if not base_prompt:
        # Handle unsupported combination
        print(f"No prompt found for type {content_type} and question type {question_type}")
        return ""

    # Build optional instructions
    subject_instruction = f"Subject: {subject}." if subject else ""
    exam_instruction = f"Reference exam: {exam}." if exam else ""
    custom_instruction_text = f"Custom instruction: {custom_instruction}." if custom_instruction else ""

    # Format the prompt
    final_prompt = base_prompt.format(
        content=content,
        level=level,
        num_of_question=num_of_question,
        subject_instruction=subject_instruction,
        exam_instruction=exam_instruction,
        custom_instruction=custom_instruction_text
    )

    return final_prompt