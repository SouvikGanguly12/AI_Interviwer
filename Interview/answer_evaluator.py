import re


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text.lower()))


def get_proper_answer(question: str) -> str:
    """Rule-based expected/proper answer text (no external AI calls)."""
    q = (question or "").lower()

    # Python decorators
    if "decorator" in q:
        return (
            "Python decorators are functions (or callables) that wrap another function. "
            "They modify behavior without changing the original function code. "
            "Typical uses: logging, authentication, caching, and enforcing pre/post conditions. "
            "A decorator usually takes a function, defines an inner wrapper, and returns the wrapper."
        )

    # list vs tuple
    if "list" in q and "tuple" in q:
        return (
            "A list is mutable (its elements can be changed) and is written with [ ]. "
            "A tuple is immutable and is written with ( ). "
            "Tuples are often used for fixed collections of values and can be slightly safer/faster due to immutability."
        )

    # generator / yield
    if "generator" in q or "yield" in q:
        return (
            "A generator is an iterator that yields values lazily. "
            "Instead of building the whole result in memory, a generator produces items one-by-one using `yield`. "
            "This is useful for large datasets, streaming, and improving memory usage."
        )

    # overfitting / bias-variance
    if "overfitting" in q:
        return (
            "Overfitting happens when a model learns noise and performs well on training data but poorly on unseen data. "
            "Common causes: too-complex model, insufficient data, or insufficient regularization. "
            "Solutions include: regularization, more data, data augmentation, early stopping, and simpler models."
        )

    if "bias-variance" in q or "bias variance" in q:
        return (
            "Bias-variance tradeoff describes two error sources: bias (errors from overly simplistic assumptions) "
            "and variance (errors from sensitivity to training data). "
            "Low bias but high variance overfits; high bias but low variance underfits. "
            "We balance them using techniques like regularization, proper model complexity, and enough (but not excessive) training."
        )

    if "linear regression" in q:
        return (
            "Linear regression models the relationship between features and a target as a weighted sum (plus intercept). "
            "It typically trains by minimizing a loss function such as mean squared error (MSE). "
            "Parameters are learned using methods like gradient descent or the normal equation."
        )

    # SQL vs MongoDB
    if "sql" in q and "mongodb" in q:
        return (
            "SQL databases use a fixed schema and provide tables/rows (relational model). "
            "MongoDB is a document database that stores JSON-like documents and can flex the schema. "
            "SQL uses joins for relationships; MongoDB often embeds data or uses references and can use aggregation for complex queries."
        )

    # MongoDB indexing
    if "index" in q:
        return (
            "Indexes in MongoDB improve query performance by allowing MongoDB to find documents faster instead of scanning the entire collection. "
            "They are built using fields (and sometimes compound keys) and come with tradeoffs: they take extra storage and slow down writes. "
            "Choosing the right indexes for frequent filters/sorts is crucial."
        )

    if "aggregation" in q or "aggregation pipeline" in q:
        return (
            "An aggregation pipeline in MongoDB is a sequence of stages that transform and process documents. "
            "It can filter (e.g., $match), group (e.g., $group), compute new fields ($project/$addFields), sort ($sort), and more. "
            "It is used to perform complex analytics within the database."
        )

    # Django MVT / ORM / auth
    if "mvt" in q or "django's mvt" in q:
        return (
            "Django uses the Model-View-Template (MVT) architecture. "
            "Model: data and database access. "
            "View: business logic and request handling. "
            "Template: presentation layer (HTML). "
            "URLs map requests to views, views use models to fetch data, then render templates."
        )

    if "django orm" in q:
        return (
            "Django ORM is a layer that lets you interact with the database using Python classes and query APIs. "
            "You define models, Django generates SQL queries, and you can use QuerySets for filtering, ordering, and aggregation. "
            "It helps avoid writing raw SQL and improves maintainability."
        )

    if "authentication" in q:
        return (
            "In Django, authentication can be implemented using built-in auth tools. "
            "Use Django’s User model and authentication views (or custom views) "
            "plus password hashing (handled automatically). "
            "For security, protect routes with login-required checks, use sessions or tokens, "
            "and validate credentials properly."
        )

    # OpenCV
    if "threshold" in q:
        return (
            "Image thresholding separates pixels into foreground/background using a cutoff value. "
            "For a binary threshold: pixels above the threshold become white, below become black. "
            "It can be global or adaptive (local thresholds) and is commonly used before contour detection."
        )

    if "haar" in q:
        return (
            "Haar Cascades perform face detection by scanning an image at multiple scales and evaluating simple features. "
            "They use a cascade of classifiers: early stages reject non-matches quickly, "
            "while later stages verify potential detections."
        )

    if "segmentation" in q and "detection" in q:
        return (
            "Segmentation assigns a label to each pixel (pixel-level output). "
            "Object detection finds bounding boxes (and often class labels) for objects in an image. "
            "Segmentation is more granular but typically more complex computationally."
        )

    # Project / certificate
    if "tell me about one project" in q:
        return (
            "A strong project answer should include: (1) the problem, (2) your role, "
            "(3) your approach/architecture, (4) the key challenge and how you solved it, "
            "(5) the results/metrics and impact, and (6) what you learned/improved."
        )

    if "hardest technical challenge" in q:
        return (
            "Describe the hardest technical challenge with specifics: what constraint made it hard, "
            "what options you considered, what you implemented, why you chose that approach, "
            "and the measurable outcome or improvement after the fix."
        )

    if "metrics" in q or "results" in q:
        return (
            "Mention measurable outcomes (e.g., accuracy, latency, throughput, conversion rate). "
            "Explain how you measured them, the baseline, and what changed due to your work."
        )

    if "certificate" in q or "certification" in q:
        return (
            "Explain which certificate/course you earned, what topics it covered, "
            "and give a concrete example of how you applied it in a project (or how it improved your workflow)."
        )

    # Default fallback
    return (
        "Give a clear, structured answer: define the concept, explain how it works, "
        "include a short example, and mention any relevant tools/techniques from your experience."
    )


def evaluate_answer(question, answer):
    """Return rubric-based evaluation.

    Returns dict:
      - score: 0-10
      - feedback: short analysis string
      - proper_answer: rule-based expected answer text
    """
    q = (question or "").lower()
    a = (answer or "").strip().lower()
    wc = _count_words(a)

    if wc < 5:
        return {
            "score": 2,
            "feedback": "Answer is too short. Try to include key concepts, an example, and what you did/learned.",
            "proper_answer": get_proper_answer(question),
        }

    # Skill questions
    if any(k in q for k in ["python", "decorator", "list", "tuple", "generator"]):
        score = 4
        feedback_bits = []

        if "python" in a:
            score += 2
            feedback_bits.append("Mentions Python explicitly.")
        if any(x in a for x in ["decorator", "decorators"]):
            score += 2
            feedback_bits.append("Covers decorators.")
        if any(x in a for x in ["generator", "yield"]):
            score += 2
            feedback_bits.append("Explains generators/yield.")

        if score >= 9:
            feedback_bits.append("Strong technical understanding.")
        else:
            feedback_bits.append("Add a more concrete explanation or a small example.\n")

        return {
            "score": min(10, score),
            "feedback": " ".join(feedback_bits).strip(),
            "proper_answer": get_proper_answer(question),
        }

    # Project questions
    if any(k in q for k in ["project", "built", "e-commerce", "face", "recognition", "opencv", "django", "mongodb"]):
        score = 4
        feedback_bits = []
        if any(x in a for x in ["problem", "challenge", "requirement"]):
            score += 2
            feedback_bits.append("States the problem/challenge clearly.")
        if any(x in a for x in ["approach", "pipeline", "model", "architecture", "technique"]):
            score += 2
            feedback_bits.append("Describes approach/architecture/technique.")
        if any(x in a for x in ["result", "improved", "accuracy", "performance", "metric"]):
            score += 2
            feedback_bits.append("Includes measurable outcome/impact.")
        if any(x in a for x in ["stack", "django", "mongodb", "opencv", "python"]):
            score += 2
            feedback_bits.append("Mentions relevant tools/stack.")

        return {
            "score": min(10, score),
            "feedback": (" ".join(feedback_bits) if feedback_bits else "Good effort—add problem, approach, and impact."),
            "proper_answer": get_proper_answer(question),
        }

    # Certificate/learning questions
    if any(k in q for k in ["certificate", "certification", "course", "learned", "training"]):
        score = 4
        feedback_bits = []
        if any(x in a for x in ["learned", "understood", "i learned", "knowledge"]):
            score += 2
            feedback_bits.append("Connects learning to understanding.")
        if any(x in a for x in ["applied", "used", "implemented", "project"]):
            score += 2
            feedback_bits.append("Explains how it was applied.")
        if any(x in a for x in ["example", "project", "use case"]):
            score += 2
            feedback_bits.append("Gives an example/use case.")
        return {
            "score": min(10, score),
            "feedback": (" ".join(feedback_bits) if feedback_bits else "Mention what the certificate covered and give an example of application."),
            "proper_answer": get_proper_answer(question),
        }

    # Generic fallback rubric
    score = 5
    if wc >= 50:
        score += 2
    if any(x in a for x in ["example", "for example", "e.g."]):
        score += 2

    return {
        "score": min(10, score),
        "feedback": "Add 1-2 concrete examples and explicitly explain the key concept(s) asked by the question.",
        "proper_answer": get_proper_answer(question),
    }

