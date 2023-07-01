#from myproject import app
from t2e_gui import app

if __name__ == "__main__":
    #app.run()
    app.run_server(host='0.0.0.0', port=8050, debug=True)
