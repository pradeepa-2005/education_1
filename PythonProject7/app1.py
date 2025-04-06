import pandas as pd

def get_recommendations(student_scores_file="student_scores.csv"):
    df = pd.read_csv(student_scores_file)

    def assign_group(score):
        if score < 50:
            return 'Beginner'
        elif 50 <= score < 75:
            return 'Intermediate'
        else:
            return 'Advanced'

    df['group'] = df['score'].apply(assign_group)

    def recommend_content(group):
        if group == 'Beginner':
            return "Watch basic concept videos + Attend remedial class"
        elif group == 'Intermediate':
            return "Practice worksheet + Group discussion"
        else:
            return "Challenge project + Peer teaching"

    df['recommended_action'] = df['group'].apply(recommend_content)

    return df[['name', 'score', 'group', 'recommended_action']].to_dict(orient='records')
