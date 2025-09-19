from app import create_app

# Variabel 'app' ini yang akan dicari oleh Vercel
app = create_app()

# Bagian di bawah ini hanya untuk menjalankan di lokal, 
# Vercel tidak akan menggunakannya.
if __name__ == '__main__':
    app.run(debug=True)