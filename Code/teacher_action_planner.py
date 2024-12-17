from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os
import time

app = Flask(__name__, template_folder='teacher_action_templates')

# Sample data representing students' performance scores
data = {
    'Student': ['Student A', 'Student B', 'Student C', 'Student D'],
    'KI_Embedded': [2, 3, 4, 1],
    'KI_Posttest': [3, 4, 5, 2],
    'Disciplinary_Embedded': [1, 2, 3, 2],
    'Disciplinary_Posttest': [2, 3, 3, 3],
    'Engineering_Analysis_Embedded': [1, 2, 1, 0],
    'Engineering_Analysis_Posttest': [2, 2, 3, 1],
}

df = pd.DataFrame(data)


# Function to generate the percentage distribution chart
def generate_percentage_histogram(scores,title,filename):
    total_students = sum(scores.values())

    # Convert the scores into percentages
    if total_students > 0:
        percentages = [(count / total_students) * 100 for count in scores.values()]
    else:
        percentages = [0] * len(scores)

    plt.figure(figsize=(10,6))

    # Update color for histogram bars
    bar_color = '#ea519e'  # Change this color to whatever you prefer
    bars = plt.bar(scores.keys(),percentages,color=bar_color,edgecolor='black')

    # Add annotations on top of each bar
    for bar,percentage,count in zip(bars,percentages,scores.values()):
        plt.text(bar.get_x() + bar.get_width() / 2,bar.get_height() + 1,f'{percentage:.2f}%',
                 ha='center',va='bottom',fontsize=10)
        plt.text(bar.get_x() + bar.get_width() / 2,bar.get_height() - 5,f'{count} Students',
                 ha='center',va='bottom',fontsize=10,color='blue')

    plt.xlabel('Scores')
    plt.ylabel('Percentage of Total Scores (%)')
    plt.title(title)
    plt.xticks(range(6))  # Ensure x-axis is labeled from 0 to 5
    plt.ylim(0,100)  # Ensure y-axis is scaled from 0 to 100
    plt.tight_layout()

    # Saving the figure
    static_folder_path = os.path.join(os.path.dirname(__file__),'static')
    if not os.path.exists(static_folder_path):
        os.makedirs(static_folder_path)

    plt.savefig(os.path.join(static_folder_path,filename))
    plt.close()


# Function to generate individual student score chart
def generate_student_scores_histogram(student_scores, student_name, filename):
    plt.figure(figsize=(10, 6))
    colors = ['#ddd4f9' if 'Embedded' in key else 'lightgreen' for key in student_scores.keys()]
    bars = plt.bar(student_scores.keys(), student_scores.values(), color=colors)

    # Add annotations on top of each bar
    for bar, score in zip(bars, student_scores.values()):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f'{score}',
                 ha='center', va='bottom', fontsize=10)

    plt.xlabel('Score Type')
    plt.ylabel('Score Value')
    plt.title(f'Scores for {student_name}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    static_folder_path = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_folder_path):
        os.makedirs(static_folder_path)

    plt.savefig(os.path.join(static_folder_path, filename))
    plt.close()

@app.route('/')
def index():
    score_data = {
        'score_type': request.args.get('score_type', 'All Scores'),
        'score_1': request.args.get('score_1', ''),
        'score_2': request.args.get('score_2', ''),
        'score_3': request.args.get('score_3', ''),
        'score_4': request.args.get('score_4', ''),
        'score_5': request.args.get('score_5', '')
    }
    return render_template('tap_dashboard.html', data=df.to_dict(orient='records'), timestamp=time.time(), score_type=score_data['score_type'], scores=score_data)

@app.route('/update_scores', methods=['POST'])
def update_scores():
    # Get form data for individual student scores
    student_id = request.form['student_id']
    student_scores = {
        'KI_Score_Embedded': int(request.form['KI_Embedded']),
        'KI_Posttest': int(request.form['KI_Posttest']),
        'Disciplinary_Embedded': int(request.form['Disc_Embedded']),
        'Disciplinary_Posttest': int(request.form['Disc_Posttest']),
        'Engineering_Analysis_Embedded': int(request.form['Eng_Anal_Embedded']),
        'Engineering_Analysis_Posttest': int(request.form['Eng_Anal_Posttest'])
    }

    # Generate the student scores histogram
    generate_student_scores_histogram(
        student_scores,
        student_id,
        'student_scores.png'
    )

    # Redirect to the main page to see the updated student graph
    return redirect(url_for('index'))

@app.route('/update_class_scores', methods=['POST'])
def update_class_scores():
    # Get form data
    score_type = request.form['score_type']
    scores = {
        1: int(request.form['score_1']),
        2: int(request.form['score_2']),
        3: int(request.form['score_3']),
        4: int(request.form['score_4']),
        5: int(request.form['score_5']),
    }

    # Generate the percentage histogram with the updated scores
    generate_percentage_histogram(
        scores,
        f'Percentage Distribution of {score_type}',
        'percentage_scores.png'
    )

    # Redirect to the main page to see the updated graph with entered data
    return redirect(url_for('index', score_type=score_type, **{f'score_{i}': scores[i] for i in scores}))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
