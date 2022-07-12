mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
<<<<<<< HEAD
" > ~/.streamlit/config.toml
=======
" > ~/.streamlit/config.toml
>>>>>>> 6b00c1fa88bad9ec17a1074fb4d7944ec1f950ef
