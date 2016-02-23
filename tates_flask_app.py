from flask import Flask, request, jsonify
import psycopg2, psycopg2.extras

DB_DSN = "host=msandb.cejfkxnescks.us-west-2.rds.amazonaws.com dbname=mydb user=dbuser password=dbpassword"

app = Flask(__name__)

@app.route('/')
def home():
    return """
<html>
  <body>
    <h1>Welcome to the Football Analytics Toolbox & API</h1>
    <h2><em> A website for exploratory football data analysis</em></h2>
    <img src="http://www.rantsports.com/nfl/files/2014/10/Antonio-Brown-MNF.jpg" alt="Antonio Brown diving catch" height="250" width="500">
    <h2>Try our DraftKings data API for the 2015 NFL Season</h2>
    <p>To use the API, append the current URL in the following way: 'api/{<em>pos</em>}/{<em>week</em>}'</p>
    <p>Where <em>pos</em> is one of the following: QB, RB, WR, TE or Def</p>
    <p>and <em>week</em> is an integer 1-17.</p>
    <p>For example, http://52.35.109.135:5000/QB/15 will give you the data for the quarterbacks in week 15.</p>
    <h5>&copy; Tate James Campbell 2016</h5>
  </body>
</html>
 """

#enter model parameters 
@app.route('/toolbox', methods=['GET','POST'])
def tools():
    return """
<html>
  <body>
    <h1>Toolbox</h1>
    <h2>1. Rushing 4 Insights - pass/rush Prediction Model</h2>
    <p>A machine learning algorithm my colleagues and I developed, try it out!</p> 
    <h4>Enter the current game conditions to predict whether the next play will be a <br> rushing play or a passing play.</h4>
    <form action="model_prediction" method="post" target ="_blank">
  Time left until end of game (in seconds):<br>
  <input type="text" name="v2" value="3600"><br><br>Down:<br>
  <input type="text" name="v3" value="1"><br><br>Distance to first down (yards):<br>
  <input type="text" name="v4" value="10"><br><br>Yard Line<br>
  <input type="text" name="v7" value="50"><br><br>Offensive Score:<br>
  <input type="text" name="v8" value="0"><br><br>Defensive Score:<br>
  <input type="text" name="v9" value="0"><br>
  <input type="submit" value="Submit">
</form>
  </body>
</html>
    """
    
# run the logistic regression model
# uses convert.json to convert strings into ints
@app.route('/model_prediction', methods=['GET', 'POST'])
def run_model():
    import json
    with open('convert.json', 'r') as fp:
        vd = json.load(fp)
    v2 = vd[request.form['v2']]
    if v2-1800>0:
        v1 = v2-1800
    else:
        v1 = 0
    v1 = v2-1800
    v3 = vd[request.form['v3']]
    v4 = vd[request.form['v4']]
    if v2<=3600 and v2>2700:
        v5 = 1
    elif v2<=2700 and v2>1800:
        v5 = 2
    elif v2<=1800 and v2>900:
        v5 = 3
    else:
        v5 = 4
    v7 = vd[request.form['v7']]
    v8 = vd[request.form['v8']]
    v9 = vd[request.form['v9']]
    v6 = v8 - v9
    v = [v1,v2,v3,v4,v5,v6,v7,v8,v9]
    w = [-0.000204567427873, -0.000387913877518, 0.646879237819,
        0.095602992261, -0.366658206558, -0.0201826358395,
        0.000821076191998, -0.0115295925119, 0.0133174758476]
    nums = [v[i]*w[i] for i in range(9)]
    logit = sum(nums)
    pass_prob = 1.0/(1.0 + (2.71828**logit))
    if pass_prob < 0.5:
        pred = 'rushing'
        prob = 100*(1.0 - pass_prob)
    else:
        pred = 'passing'
        prob = 100*pass_prob

    prediction = "According to our model, there is a %2.1f %% chance that the next play will be a %s play" % (prob, pred)
    return prediction
    
    
# api method 1 
@app.route('/api/<pos>/<week>')
def get_qbs(pos, week):
    """
    retrieves fantasy performances for all players in the NFL for a specified position and week
    :return: a dict of all kv pairs, key = player and value = points, home_or_away, opponent
    """
    out = dict()
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute("""SELECT player,week, pos,dk_points,home_or_away, opponent from dk_stats where pos = %s and week = %s;""", (str(pos), str(week)))
    except Exception as e:
        pass
    rows = cur.fetchall()
    for row in rows:
        out[row[0]] = {"dk_points" : row[3], "home_or_away" : row[4], "opponent" : row[5]}
    return jsonify(out)
    
    
# api method 2 
@app.route('/api/<first_name>/<last_name>')
def index(first_name, last_name):
    player = last_name + ', ' + first_name
    out = dict()
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        cur.execute("""SELECT * from dk_stats where player = %s;""", (player,))
    except Exception as e:
        pass
    rows = cur.fetchall()
    for row in rows:
        out[row[0]] = row
    return out



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
    #app.debug()
