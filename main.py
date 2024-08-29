
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

'''
from website import create_app

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000, connection_limit=100, channel_timeout=600)
'''
