from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
app = Flask(__name__)

# Initialize OpenAI client with  key
client = OpenAI(api_key="your api key")
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# rendreing html page
@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        return "File has been uploaded."
    return render_template('index.html', form=form)
#generate_flowchart route for later use in html generation
@app.route('/generate_flowchart', methods=['POST'])
def generate_flowchart():
    #getting values from json object for use in prompt
    data = request.json
    topic = data.get('topic')
    nodes = data.get('nodes')
    edges = data.get('edges')

    prompt = f"""
   Generate Mermaid flowchart code about '{topic}' with {nodes} nodes and {edges} edges.  
Start with `graph direction of your choice`, where direction is one of LR, TB, TD, BT, RL.  
Output ONLY the Mermaid code with no additional text, explanation, or markdown code fences.  
Do NOT include 'mermaid', 'flowchart', or any other header or footer—just the raw code starting with the graph declaration line.  
Use syntax like:  
graph LR  
  A[Start] --> B[Learn Concepts]  
  B --> C[Practice Problems]  
End with the last edge; do not add anything after.
make it vary in shape a lot of different shapes and have like doted arrows if you want or you can have double arrows like <--> etc... and vary in different background color and vary in the orientation like TB LR etc... other orientations in mermaid."""

    #calls chat ai api to create conversation with these info
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    #setting mermaid code to the first response of the ai
    mermaid_code = response.choices[0].message.content.strip()
    #puts it into json to be rendered in html
    return jsonify({"mermaid_code": mermaid_code})

@app.route('/hand_drawn', methods=['POST'])
def hand_drawn():
    data = request.json
    topic = data.get('topic')
    nodes = data.get('nodes')
    edges = data.get('edges')

    prompt = f"""
    Provide a list of nodes and edges for a flowchart about '{topic}' with {nodes} nodes and {edges} edges.
    Include node color, shape, and edge direction but don't specify layout positions.
    Format as a text list suitable for flowcharts, no Mermaid code.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    #puts into json to be dealt with in html
    flowchart_list = response.choices[0].message.content.strip()
    return jsonify({"flowchart_list": flowchart_list})


if __name__ == '__main__':
    app.run(debug=True)
