from codeupload import create_app


app = create_app()
if __name__ == "__main__":
    print(app.config)
    app.run(debug=True)