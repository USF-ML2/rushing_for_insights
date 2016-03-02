from flask import Flask, request, jsonify, render_template
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
    <p>For example, http://52.35.109.135:5000/api/QB/15 will give you the data for the quarterbacks in week 15.</p>
    <h5>&copy; Tate James Campbell 2016</h5>
  </body>
</html>
 """

# enter model parameters
@app.route('/toolbox', methods=['GET', 'POST'])
def tools():
    return render_template('predict.html')

# run the logistic regression model
# uses convert.json to convert strings into ints
@app.route('/model_prediction', methods=['GET', 'POST'])
def run_model():
    import pickle 
    teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 
    'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAC', 'KC', 'MIA', 'MIN', 'NE',
    'NO', 'NYG', 'NYJ', 'OAK', 'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL',
    'TB', 'TEN', 'WAS', '', 'AFC', 'NFC']
    team_dict = dict()
    i = 0
    for t in teams:
        vec = np.zeros(len(teams))
        vec[i] = 1
        team_dict[t] = vec
        i += 1
    print request.form
    # Request.form is a immutablemultidict so convert it to a nicer dict
    form_data = {k: int(v[0]) for (k, v) in request.form.items()}
    vars_from_req = ['time_left_in_game', 'down_num', 'dist_to_first', 'yard_line',
        'off_team', 'off_score', 'def_team', 'def_score']
    varS = {v : form_data[v] for v in vars_from_req}
    if varS['time_left_in_game'] - 1800 > 0:
        varS['time_to_half'] = varS['time_left_in_game'] - 1800
    else:
        varS['time_to_half'] = varS['time_left_in_game']
    # Now just use form_data['v1'] etc
    if varS['time_left_in_game'] <= 3600 and varS['time_left_in_game'] > 2700:
        varS['quarter'] = 1
    elif varS['time_left_in_game'] <= 2700 and varS['time_left_in_game'] > 1800:
        varS['quarter'] = 2
    elif varS['time_left_in_game'] <= 1800 and varS['time_left_in_game'] > 900:
        varS['quarter'] = 3
    elif varS['time_left_in_game'] <= 900 and varS['time_left_in_game'] >= 0:
        varS['quarter'] = 4
    else:
        varS['quarter'] = 5
    varS['score_diff'] = varS['off_score'] - varS['def_score']
    off_vec = team_dict[varS['off_team']]
    def_vec = team_dict[varS['def_team']]
    X1 = [varS['time_to_half'], varS['time_left_in_game'], varS['down_num'],
        varS['dist_to_first'], varS['quarter'], varS['score_diff'], 
        varS['yard_line'], varS['off_score'], varS['def_score']]
    X = X1 + off_vec + def_vec
    with open('pickled_football_models/logreg_model.txt') as lr:
        lr_clf = pickle.load(lr)
    pred = lr_clf.predict(X)
    # pass_prob = 1.0/(1.0 + (2.71828**logit))
    # if pass_prob < 0.5:
    #     pred = 'rushing'
    #     prob = 100*(1.0 - pass_prob)
    # else:
    #     pred = 'passing'
    #     prob = 100*pass_prob

    #prediction = "According to our model, there is a %2.1f %% chance that the next play will be a %s play" % (prob, pred)
    return pred


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
    app.run(host = '0.0.0.0', port = 5000, debug=True)
    #app.debug()
